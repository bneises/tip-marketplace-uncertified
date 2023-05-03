import magic
import hashlib
import typing
import os
import base64
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime,  add_prefix_to_dict, dict_to_flat
from SiemplifyDataModel import Attachment
import re
import zipfile
import io
import time



ORIG_EMAIL_DESCRIPTION = "This is the original message as EML"
EXTEND_GRAPH_URL = '{}/external/v1/investigator/ExtendCaseGraph'
CASE_DETAILS_URL = '/external/v1/cases/GetCaseFullDetails/'


            

class AttachmentsManager(object):
    def __init__(self, siemplify):
        
        self.siemplify = siemplify
        self.logger = siemplify.LOGGER
        self.alert_entities = self.get_alert_entities()
        pass
    
    
    def get_alert_entities(self):
        return [entity for alert in self.siemplify.case.alerts for entity in alert.entities]

    def get_attachments(self):
        response = self.siemplify.session.get(f'{self.siemplify.API_ROOT}{CASE_DETAILS_URL}' + self.siemplify.case.identifier)
        wall_items = response.json()['wallData']
        attachments = []
        for wall_item in wall_items:
            if wall_item['type'] == 4:
                if not wall_item['alertIdentifier']:
                    attachments.append(wall_item)
                    
        return attachments        
        
    def get_alert_attachments(self):
        response = self.siemplify.session.get(f'{self.siemplify.API_ROOT}{CASE_DETAILS_URL}' + self.siemplify.case.identifier)
        wall_items = response.json()['wallData']
        attachments = []
        for wall_item in wall_items:
            if wall_item['type'] == 4:
                if self.siemplify.current_alert.identifier == wall_item['alertIdentifier']:
                    attachments.append(wall_item)
        return attachments
            
        
    def add_attachment(self, filename,  base64_blob, case_id, alert_identifier, description=None, is_favorite=False):
        """
        add attachment
        :param file_path: {string} file path
        :param case_id: {string} case identifier
        :param alert_identifier: {string} alert identifier
        :param description: {string} attachment description
        :param is_favorite: {boolean} is attachment favorite
        :return: {dict} attachment_id
        """
        name, attachment_type = os.path.splitext(os.path.split(filename)[1])
        if not attachment_type:
            attachment_type = ".noext"
        attachment = Attachment(case_id, alert_identifier, base64_blob, attachment_type, name, description, is_favorite, len(base64.b64decode(base64_blob)), len(base64_blob))
        attachment.case_identifier = case_id
        attachment.alert_identifier = alert_identifier
        address = "{0}/{1}".format(self.siemplify.API_ROOT, "external/v1/sdk/AddAttachment?format=snake")
        response = self.siemplify.session.post(address, json=attachment.__dict__)
        try:
            self.siemplify.validate_siemplify_error(response)
        except Exception as e:
            if "Attachment size" in e.message:
                raise Exception("Attachment size should be < 5MB. Original file size: {0}. Size after encoding: {1}.".
                                format(attachment.orig_size, attachment.size))
        return response.json()
        
    def create_file_entities(self,  attachments):
        new_entities_w_rel = {}
        updated_entities = []
        for file_entity in attachments:
            entity_identifier = str(file_entity['filename'].strip()).upper()
            
            try:
                properties = {}
                properties = dict_to_flat(file_entity)
                del properties['filename']
                if 'parent_file' in properties:
                    self.logger.info(f"creating with relation: {entity_identifier} to {properties['parent_file']}")
                    self.create_entity_with_relation(entity_identifier, properties['parent_file'].upper(), entity_type="FILENAME")
                    new_entities_w_rel[entity_identifier] = properties
                else:
                    name, attachment_type = os.path.splitext(entity_identifier)
                    found = 0
                    for alert_entity in self.alert_entities:
                        if alert_entity.identifier == name.upper() and alert_entity.entity_type == "EMAILSUBJECT":
                            self.create_entity_with_relation(entity_identifier, alert_entity.identifier, entity_type="FILENAME")
                            new_entities_w_rel[entity_identifier] = properties
                            found = 1
                            break
                    if found == 0:
                        self.logger.info(f"Creating entity: {entity_identifier} without relationship.")
                        self.siemplify.add_entity_to_case(entity_identifier, "FILENAME", False, False,
                                                True, False, properties)
            except Exception as e:
                self.logger.error(e)
                raise
            self.logger.info(f"Creating entity: {properties['hash_md5']} and linking it to f{entity_identifier}.")
            self.create_entity_with_relation(properties['hash_md5'], entity_identifier, entity_type="FILEHASH")
            
        if new_entities_w_rel:
            self.siemplify.load_case_data()
            time.sleep(3)
            for new_entity in new_entities_w_rel:
                for entity in self.get_alert_entities():
                    if new_entity.strip() == entity.identifier.strip():
                        entity.additional_properties.update(new_entities_w_rel[new_entity])
                        updated_entities.append(entity)
                        break
            self.logger.info(f"updating entities: {updated_entities}")
            self.siemplify.update_entities(updated_entities)        
            
    def check_if_entity_exists(self, entity_identifier):
        """
        Verify if entity with such identifier already exists within the case.

        :param target_entities: enumeration of case entities (e.g. siemplify.target_entities)
        :param entity_identifier: identifier of entity, which we're checking
        :return: True if entity with such identier exists already within case; False - otherwise
        """
        for entity in self.alert_entities:
            if entity.identifier.strip() == entity_identifier:
                return True
        return False
    
    def create_entity_with_relation(self, new_entity, linked_entity, entity_type="FILENAME"):
        json_payload = {
            "caseId": self.siemplify.case_id,
            "alertIdentifier": self.siemplify.alert_id,
            "entityType": "{}".format(entity_type),
            "isPrimaryLink": False,
            "isDirectional": False,
            "typesToConnect": [],
            "entityToConnectRegEx": "{}$".format(re.escape(linked_entity.upper())),
            "entityIdentifier": new_entity.upper()
        }
        payload = json_payload.copy()
        created_entity = self.siemplify.session.post(EXTEND_GRAPH_URL.format(self.siemplify.API_ROOT), json=json_payload)
        created_entity.raise_for_status()
        
    def extract_zip(self,zip_filename, content, bruteforce=False, pwds=None):
        with zipfile.ZipFile(content) as attach_zip:
            extracted_files = []
            try:
                for name in attach_zip.namelist():
                    extracted_file = self.attachment(name, attach_zip.read(name))
                    extracted_file['parent_file'] = zip_filename
                    extracted_files.append(extracted_file)
                return extracted_files
            except:
                pass
            pwd = None
            if bruteforce:
                from wordlist import wordlist
                for line in io.StringIO(wordlist.WORDLIST).readlines():
                    password = line.strip("\n")
                    try:
                        attach_zip.setpassword(password.encode()) 
                        for name in attach_zip.namelist():
                            _file = attach_zip.read(name)
                            pwd = password
                            self.logger.info(f"Password found {pwd}")
                            break
                        break
                    except:
                        pass
                        
                        
            if pwds and pwd == None:
                try:
                    found = 0
                    for passwd in pwds:
                        try:
                            attach_zip.setpassword(passwd.encode())
                            for name in attach_zip.namelist():
                                _file = attach_zip.read(name)
                                pwd = passwd
                                self.logger.info(f"Password found {pwd}")
                                found = 1
                                break
                            if found == 1:
                                break
                        except Exception as e:
                            pass
                except:
                    raise
                
            try:
                for name in attach_zip.namelist():
                    extracted_file = self.attachment(name, attach_zip.read(name))
                    extracted_file['parent_file'] = zip_filename
                    extracted_files.append(extracted_file)
                return extracted_files
            except RuntimeError:
                raise
            
            


    @staticmethod
    def get_file_hash(data: bytes) -> typing.Dict[str, str]:
        """Generate hashes of various types (``MD5``, ``SHA-1``, ``SHA-256``, ``SHA-512``)\
        for the provided data.

        Args:
          data (bytes): The data to calculate the hashes on.

        Returns:
          dict: Returns a dict with as key the hash-type and value the calculated hash.
        """
        hashalgo = ['md5', 'sha1', 'sha256', 'sha512']
        hash_ = {}

        for k in hashalgo:
            ha = getattr(hashlib, k)
            h = ha()
            h.update(data)
            hash_[k] = h.hexdigest()

        return hash_
        
   

    @staticmethod
    def get_mime_type(data: bytes) -> typing.Union[typing.Tuple[str, str], typing.Tuple[None, None]]:
        """Get mime-type information based on the provided bytes object.

        Args:
            data: Binary data.

        Returns:
            typing.Tuple[str, str]: Identified mime information and mime-type. If **magic** is not available, returns *None, None*.
                                    E.g. *"ELF 64-bit LSB shared object, x86-64, version 1 (SYSV)", "application/x-sharedlib"*
        """
        if magic is None:
            return None, None

        detected = magic.detect_from_content(data)
        return detected.name, detected.mime_type
    
    @staticmethod
    def attachment(filename, content):
        mime_type, mime_type_short = AttachmentsManager.get_mime_type(content)
        attachment_json = {
            'filename': filename,
            'size': len(content),
            'extension': os.path.splitext(filename)[1][1:],
            'hash': {
                'md5': hashlib.md5(content).hexdigest(),
                'sha1': hashlib.sha1(content).hexdigest(),
                'sha256': hashlib.sha256(content).hexdigest(),
                'sha512': hashlib.sha512(content).hexdigest()
            },
            'mime_type': mime_type,
            'mime_type_short': mime_type_short,
            'raw': base64.b64encode(content).decode()
        }
        return attachment_json        
   
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            