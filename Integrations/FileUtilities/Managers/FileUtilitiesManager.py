from filelock import FileLock


class EntityFileManagerException(Exception):
    pass


class EntityFileManager:
    def __init__(self, filepath, timeout=None):
        """
        Initiate the manager. This will create a file.lock in the same folder as the filepath. 
        :param filepath:
        :param timeout:
        """
        self.filepath = filepath
        self.timeout = timeout

        self.lockpath = self.filepath + ".lock"
        if self.timeout:
            self.lock = FileLock(self.lockpath, timeout=self.timeout)
        else:
            self.lock = FileLock(self.lockpath)
        self.entities = []

    def __enter__(self):
        """
        This function is executed with a "with" statement. It will acquire the lock, and block other processes from 
        using this file (only if it's using py-filelock or check the .lock file). Once locked, it will fetch the rows
        from the file to self.entities to make changes. 
        :return:
        """
        self.lock.acquire()
        self.entities = self.readFile()
        return self

    def __exit__(self, typ, value, traceback):
        """
        This function is executed in the end of the "with" statement. It will write the changed to the file and release 
        the lock. All parameters are built-ins of python and are not required.
        :param typ: Ignore.
        :param value: Ignore.
        :param traceback: Ignore.
        """
        self.writeFile()
        self.lock.release()

    def readFile(self):
        """
        Helper function to read all entities from the file.
        :return: List with file contents (Entity Identifiers)
        """
        try:
            with open(self.filepath, 'r') as f:
                data = f.readlines()
            return [x.strip() for x in data]
        except FileNotFoundError:
            return []

    def writeFile(self):
        """
        Helper function to write the entities list to the file
        """
        with open(self.filepath, 'w') as f:
            f.write('\n'.join(self.entities))

    def addEntity(self, entity):
        """
        Add elements to self.entities list
        :param entity: Entity identifier
        :return: True
        """
        self.entities.append(entity)
        return True

    def removeEntity(self, entity):
        """
        Remove elements from self.entities list
        :param entity: Entity identifier
        :return: True
        """
        try:
            self.entities.remove(entity)
            return True
        except KeyError:
            raise EntityFileManagerException("Entity not found in file")
