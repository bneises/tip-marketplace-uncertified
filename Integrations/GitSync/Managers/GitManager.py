import base64
import os
import shutil
import stat
from io import StringIO
from typing import List

import paramiko.rsakey
from dulwich import client as _mod_client
from dulwich import porcelain
from dulwich.contrib.paramiko_vendor import _ParamikoWrapper
from dulwich.contrib.requests_vendor import RequestsHttpGitClient
from dulwich.errors import HangupException, GitProtocolError
from dulwich.object_store import tree_lookup_path
from dulwich.objects import Blob, Tree
from dulwich.refs import HEADREF, LOCAL_BRANCH_PREFIX
from dulwich.repo import Repo
from paramiko.ssh_exception import SSHException

from definitions import File


class Git:
    """Wrapper for Dulwich - Git Manager"""

    def __init__(self, repo_url, branch_name, working_directory, password, username, author, verify_ssl, logger):
        """Wrapper for dulwich - a pure python git client.

        Args:
            repo_url (str): repository url. SSH and HTTP urls are supported
            branch_name (str): name of the target branch to push or pull changes from
            working_directory (str): path to local directory to clone or store the repo
            password (str): Api token, SSH key (base64 encoded) or user's password
            username (str): Username. Not used when connecting to a repo using SSH
            author (str): Commit author. Must be in the following format: James Bond <james.bond@gmail.com>
            verify_ssl (bool): Whether to verify SSL with the git provider
            logger (Logger): A logger instance
        """
        self.logger = logger
        self.repo_url = repo_url
        self.branch_name = branch_name.encode('utf-8')
        self.local_branch_ref = b'refs/heads/' + self.branch_name
        self.remote_branch_ref = b"refs/remotes/origin/" + self.branch_name
        self.wd = working_directory
        self.username = username
        self.password = password
        self.author = author
        self.verify_ssl = verify_ssl

        if self.repo_url.startswith("ssh://") or self.repo_url.startswith("git@"):
            # When using ssh - the username is ignored
            self.connection_args = {
                "password": self.convert_password_to_private_key()
            }
        else:
            self.connection_args = {
                "username": self.username,
                "password": self.password
            }

        # Check if the git repo is present and pull changes. Otherwise, clone the repo.
        if os.path.isdir(self.wd) and os.path.isdir(os.path.join(self.wd, ".git")):
            self.repo = Repo(self.wd)
            config = self.repo.get_config()
            if config.get_boolean(b'http', b'sslVerify') != self.verify_ssl:
                self.logger.info("Git Verify SSL parameter changed. Writing new value")
                config.set(b"http", b"sslVerify", b"true" if self.verify_ssl else b"false")
                config.write_to_path()
            self.logger.info("Found existing repo. Pulling Repo Changes")
            self.pull()
        else:
            self.logger.info(f"Couldn't find repo. Cloning from {self.repo_url}")
            self._clone()
        
        if self.local_branch_ref != self.repo.refs.get_symrefs()[HEADREF]:
            self.logger.info(f"Git branch paramaeter changed, checking out branch {self.branch_name.decode()}")
            # Branch changed, checking out
            self._checkout()

        self.tree = self.get_head_tree()

    @property
    def head(self):
        """Current repo HEAD commit

        Returns:
            Commit: the HEAD commit object
        """
        return self.repo.get_object(self.repo.get_refs()[HEADREF])

    def get_head_tree(self):
        return self.repo.get_object(self.head.tree)

    @property
    def branch_tree(self):
        """Get the current branch tree.
        Used to diff between self.tree to see if any changes where made.

        Returns:
            Tree: Current branch tree
        """
        branch_sha = self.repo.get_refs()[self.local_branch_ref]
        return self.repo.get_object(self.repo.get_object(branch_sha).tree)

    def commit_and_push(self, message):
        """Create a commit and push based on current tree

        Args:
            message (str): Commit message
        """
        if self.branch_tree.id != self.tree.id:
            self.logger.info(f"Committing tree {self.tree.id} with message {message}")
            self.repo.do_commit(tree=self.tree.id, message=message.encode('utf-8'),
                                author=self.author.encode('utf-8'))
            self.push()
        else:
            self.logger.info("No changes found. Nothing to commit.")

    def pull(self):
        """Pulls changes from the repo. We ignore conflicts and reset local repo to the origin one.
        """
        remote_refs = porcelain.fetch(self.repo, **self.connection_args)
        for key, value in remote_refs.items():
            self.repo.refs[key] = value

    def push(self, force_push=False):
        """Push current branch to the repo

        Args:
            force_push (bool, optional): If set to True, the push will overwrite remote objects, equivilent to 'git push --force'. Defaults to False.
        """
        porcelain.push(
            self.repo,
            refspecs=[self.local_branch_ref],
            force=force_push,
            **self.connection_args
        )

    def _checkout(self):
        """Checkout branch
        First it will checkout a remote branch if exists
        If it doesn't exitst, It will use the remote HEAD as a base to a new branch
        If it doesn't exists, It will use local branch as base for a new branch
        If it doesn't exists, It assums the repository is empty and creates an initial commit and branch
        """
        if self.remote_branch_ref in self.repo.refs:
            # Checkout remote branch
            self.logger.info("Checking out remote branch")
            self.repo.refs.add_if_new(self.local_branch_ref, self.repo.refs[self.remote_branch_ref])
        elif b"refs/remotes/origin/HEAD" in self.repo.refs:
            # No local HEAD - Use remote HEAD
            self.logger.info("Creating new local branch using remote HEAD")
            self.repo.refs.add_if_new(self.local_branch_ref, self.repo.refs[b"refs/remotes/origin/HEAD"])
        elif HEADREF in self.repo.get_refs():
            # New branch - use local head as base
            self.logger.info("Creating new local branch using local HEAD")
            self.repo.refs.add_if_new(self.local_branch_ref, self.head.id)
        else:
            # Empty repo
            self.logger.info("Empty repo, creating branch from scratch")
            blob = Blob.from_string(b"# GitSync\n")
            self.repo.object_store.add_object(blob)
            tree = Tree()
            tree.add(b"README.md", stat.S_IFREG | 0o644, blob.id)
            self.repo.object_store.add_object(tree)
            commit = self.repo.do_commit(b"Intial commit", tree=tree.id, ref=None)
            self.repo.refs[self.local_branch_ref] = commit
            self.push()

        self.repo.refs.set_symbolic_ref(HEADREF, self.local_branch_ref)
        self.repo.refs.set_if_equals(HEADREF, None, self.repo.refs[self.local_branch_ref])

    def _clone(self):
        """Clones a git repository from repo url.
        """
        if not os.path.exists(self.wd):
            os.mkdir(self.wd)

        self.repo = Repo.init(self.wd)
        try:
            config = self.repo.get_config()
            config.set((b"remote", b"origin"), b"url", self.repo_url.encode('utf-8'))
            config.set((b"remote", b"origin"), b"fetch", b"+refs/heads/*:refs/remotes/origin/*")
            config.set(b"http", b"sslVerify", b"true" if self.verify_ssl else b"false")
            config.write_to_path()

            fetch_results = porcelain.fetch(self.repo, **self.connection_args)

            origin_head_ref = fetch_results.symrefs.get(HEADREF)
            origin_head_sha = fetch_results.refs.get(HEADREF)

            if origin_head_sha and not origin_head_ref:
                # set detached HEAD
                self.repo.refs[HEADREF] = origin_head_sha

            # Set remote HEAD symbolic ref
            # refs/remotes/origin/HEAD => refs/remotes/origin/<remote branch name>
            origin_base = b"refs/remotes/origin/"
            origin_ref = origin_base + HEADREF
            # Check if remote has HEAD
            if origin_head_ref and origin_head_ref.startswith(LOCAL_BRANCH_PREFIX):
                target_ref = origin_base + origin_head_ref[len(LOCAL_BRANCH_PREFIX) :]
                if target_ref in self.repo.refs:
                    self.repo.refs.set_symbolic_ref(origin_ref, target_ref)
            
            self._checkout()
            
        except BaseException:
            shutil.rmtree(self.wd)
            self.repo.close()
            raise

    def update_objects(self, files: List[File], tree=None, base_path=b''):
        """Main method to edit objects in the repo.
        
        Args:
            files (List[File]): A list or generator of File objects
            tree (Tree, optional): The base tree which gets updated. If not supplied, will use current HEAD tree
            base_path (bytes, optional): Relative path in the repo. If supplied - All files under that base will be deleted/overwritten.
                          If not supplied, files parameter elements must be with absolute paths. Files will not be deleted, but will be overwritten. Defaults to root path.

        Returns:
            Tree: The modified tree
        """
        if not tree:
            self.tree = self._modify_tree(files, self.tree, base_path)
            return self.tree
        else:
            return self._modify_tree(files, tree, base_path)


    def _modify_tree(self, files: List[File], tree, base_path=b''):
        """Modifies a given tree, recursivly, and adds all objects to the repo.object_store

        Args:
            files (List[File]): A list or generator of File objects
            tree (Tree): A tree object to update
            base_path (bytes, optional): Relative path in the repo. If supplied - All files under that base will be deleted/overwritten. Defaults to root path.

        Returns:
            Tree: The modified tree
        """
        try:
            _, subtree = tree.lookup_path(lambda sha: self.repo[sha], base_path.split(b"/")[0])
            subtree = self.repo[subtree]
        except KeyError:
            subtree = Tree()

        if not base_path:
            new_tree = self._create_raw_tree(files, tree)
            self.repo.object_store.add_object(new_tree)
            return new_tree

        base_path = base_path.split(b"/")
        folder_name = base_path.pop(0)
        base_path = b'/'.join(base_path)
        if not base_path:
            # New Directory
            new_tree = self._create_raw_tree(files)
        else:
            new_tree = self._modify_tree(files, subtree, base_path)
        self.repo.object_store.add_object(new_tree)
        tree.add(folder_name, stat.S_IFDIR, new_tree.id)
        return tree

    def _create_raw_tree(self, files, tree=None):
        """It is recommended to use the function update_objects.
        Creates a new tree object or updates the one passed down to it.
        If a tree object is passed down it will inherit all the other objects and won't delete files.

        Args:
            files (List[Files]): list or generator of Files object
            tree (Tree, optional): Tree to modify. if not passed, it will create a new tree. Defaults to None.

        Returns:
            Tree: The new tree
        """
        if not tree:
            tree = Tree()
        for file in files:
            mode = stat.S_IFREG | 0o644
            obj = Blob()
            obj.data = file.content
            path_items = file.path.encode('utf-8').split(b'/')
            sub_tree = tree
            old_trees = [sub_tree]
            for name in path_items[:-1]:
                try:
                    _, sub_tree_sha = sub_tree[name]
                except KeyError:
                    sub_tree = Tree()
                else:
                    sub_tree = self.repo.get_object(sub_tree_sha)
                old_trees.append(sub_tree)

            for old_tree, name in reversed(tuple(zip(old_trees, path_items))):
                old_tree[name] = (mode, obj.id)
                self.repo.object_store.add_object(obj)
                obj = old_tree
                mode = stat.S_IFDIR

            self.repo.object_store.add_object(obj)
            tree = obj

        return tree

    def get_raw_object_from_path(self, path, tree=None):
        """Get the raw object from the git object store (Blob, Tree)

        Args:
            path (AnyStr): The path to the file
            tree (Tree, optional): The relevant tree. if not supplied the HEAD tree will be used. Defaults to None.

        Raises:
            KeyError: Raised if file or folder wasn't found

        Returns:
            (object): Raw dulwich object (Tree, Blob)
        """
        if isinstance(path, str):
            path = path.encode('utf-8')
        if tree is None:
            tree = self.tree
        try:
            return self.repo.get_object(tree_lookup_path(self.repo.get_object, tree.id, path)[1])
        except KeyError as e:
            raise KeyError(f"Couldn't find folder or file: {e}")

    def get_file_objects_from_path(self, path, tree=None):
        """Get a list of File objects from a path

        Args:
            path (AnyStr): Path to get File from
            tree (Tree, optional): Base tree to look for files. If not passed will use HEAD tree. Defaults to None.

        Returns:
            List[Files]: All files inside the given path
        """
        tree = self.get_raw_object_from_path(path, tree)
        files = []
        for file in self.repo.object_store.iter_tree_contents(tree.id, True):
            if file.mode == stat.S_IFREG | 0o644:
                files.append(File(file.path.decode('utf-8'), self.repo.object_store.get_raw(file.sha)[1]))
        return files

    def get_file_contents_from_path(self, path, tree=None):
        """Get a specific file contents from a path

        Returns:
            bytes: File contents
        """        
        return self.repo.object_store.get_raw(self.get_raw_object_from_path(path, tree).id)[1]

    def convert_password_to_private_key(self):
        """If the password parameter is a private key, we convert it to a key object that paramiko can handle

        Raises:
            Exception: Raised if the key can't be converted to RSA or Ed25519 Key

        Returns:
            Paramoiko Key: Private key object
        """
        self.password = base64.b64decode(self.password).decode('utf-8')
        try:
            return paramiko.rsakey.RSAKey.from_private_key(StringIO(self.password))
        except SSHException:
            try:
                return paramiko.ed25519key.Ed25519Key.from_private_key(StringIO(self.password))
            except SSHException as e:
                raise Exception(e)

    def list_files(self):
        """Prints list of files in the repo, recursive.
        """
        for file in self.repo.object_store.iter_tree_contents(self.tree.id):
            self.logger.info(file)


class SiemplifyParamikoSSHVendor:
    def __init__(self, **kwargs):
        """SSH client for dulwich that supports private keys instead of user:password
        """
        self.kwargs = kwargs

    def run_command(
            self,
            host,
            command,
            username=None,
            port=None,
            password=None,
            key_filename=None,
            **kwargs
    ):

        client = paramiko.SSHClient()

        connection_kwargs = {"hostname": host}
        connection_kwargs.update(self.kwargs)
        if username:
            connection_kwargs["username"] = username
        if port:
            connection_kwargs["port"] = port
        if password:
            connection_kwargs["pkey"] = password
        if key_filename:
            connection_kwargs["key_filename"] = key_filename
        connection_kwargs.update(kwargs)

        policy = paramiko.client.MissingHostKeyPolicy()
        client.set_missing_host_key_policy(policy)
        client.connect(**connection_kwargs)
        channel = client.get_transport().open_session()
        channel.exec_command(command)

        return _ParamikoWrapper(client, channel)


def remote_error_from_stderr(stderr):
    """Patch for dulwich error handling in newer paramiko versions"""
    if stderr is None:
        return HangupException()
    lines = [line.rstrip("\n") for line in stderr.readlines()]
    for line in lines:
        if line.startswith("ERROR: "):
            return GitProtocolError(line[len("ERROR: "):])
    try:
        return HangupException(lines)
    except AttributeError:
        return HangupException([line.encode('utf-8') for line in lines])


# dulwich patch to add requests support : https://github.com/jelmer/dulwich/pull/933
_mod_client.HttpGitClient = RequestsHttpGitClient
# dulwich patch to add paramiko support (can't pass pkey parameter)
_mod_client.get_ssh_vendor = SiemplifyParamikoSSHVendor
# dulwich patch to newer paramiko versions returning string and not bytes
_mod_client._remote_error_from_stderr = remote_error_from_stderr