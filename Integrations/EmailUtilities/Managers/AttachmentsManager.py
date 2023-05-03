from SiemplifyUtils import unix_now, convert_unixtime_to_datetime,  add_prefix_to_dict, dict_to_flat
from SiemplifyDataModel import Attachment
import os
import base64

ORIG_EMAIL_DESCRIPTION = "This is the original message as EML"
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
        
  


    
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            