#from TIPCommon import extract_script_param
from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED, EXECUTION_STATE_TIMEDOUT
#from EmailDataModelTransformationLayer import EmailDataModelTransformationLayer


class BaseEmailAction(object):
    """
    Abstract class for Email actions
    """
    # Constants related to Email integration config
    INTEGRATION_NAME = u"SendGrid"
    JOIN_DELIMITER = u", "
    MAX_IDS_PRINT = 100

    def __init__(self, script_name):
        """
        Base constructor. It should trigger load of entire integration configuration
        and configuration specific to the current action.
        :param script_name: {str} Name of the current action
        """
        # SiemplifyAction allows us to access many goodies,
        # which Siemplify Platform provides us on an Action level
        self.siemplify = SiemplifyAction()
        self.siemplify.script_name = script_name
        self.logger = self.siemplify.LOGGER

        self.logger.info(u"================= Main - Param Init =================")

        self.load_integration_configuration()
        #self.load_action_configuration()

    #def _get_integration_param(self, param_name, default_value=None, input_type=unicode, is_mandatory=False, print_value=False):
    #    conf = self.siemplify.get_configuration(BaseEmailAction.INTEGRATION_NAME)
    #    return extract_script_param(
    #        siemplify=self.siemplify,
    #        input_dictionary=conf,
    #        param_name=param_name,
    #        default_value=default_value,
    #        input_type=input_type,
    #        is_mandatory=is_mandatory,
    #        print_value=print_value)
    
    #def _get_action_param(self, param_name, default_value=None, input_type=unicode, is_mandatory=False, print_value=False):
    #    conf = self.siemplify.parameters
    #    return extract_script_param(
    #        siemplify=self.siemplify,
    #        input_dictionary=conf,
    #        param_name=param_name,
    #        default_value=default_value,
    #        input_type=input_type,
    #        is_mandatory=is_mandatory,
    #        print_value=print_value)

    def load_integration_configuration(self):
        """
        Protected method, which should load configuration, specific to entire Email configuration
        """
        # Load Email integration configuration
        self.load_base_integration_configuration()

    # noinspection PyAttributeOutsideInit
    def load_base_integration_configuration(self):
        """
        Loads base integration configuration, which is used by all Email integration actions
        """
        configurations = self.siemplify.get_configuration('SendGrid')
        self.api_token = configurations['API Token']
        
        self.email_from = self.siemplify.parameters.get('Email From')
        self.email_to = self.siemplify.parameters.get('Email To')
        self.subject = self.siemplify.parameters.get('Subject')
        self.content = self.siemplify.parameters.get('Content')
        self.return_message_status = self.siemplify.parameters.get('Return Message Status')

    def load_action_configuration(self):
        """
        Protected method, which should load configuration, specific to the specific Email Action
        """
        raise NotImplementedError()

    def run(self):
        """
        Main Email action method. It wraps some common logic for actions
        """
        self.logger.info(u"----------------- Main - Started -----------------")

        try:
            status = EXECUTION_STATE_COMPLETED  # Used to flag back to Siemplify system, the action final status
            output_messages = [u"Output messages:\n"]  # Human-readable message, showed in UI as the action result
            result_value = False  # Set a simple result value, used for playbook if\else and placeholders.
            failed_entities = []  # If this action contains entity based logic, collect failed entity.identifiers
            successful_entities = []  # If this action contains entity based logic, collect successful entity.identifiers

            status, result_value = self.execute_action(output_messages, successful_entities, failed_entities)

        except Exception as e:
            self.logger.error(u"General error performing action {}".format(self.SCRIPT_NAME))
            self.logger.exception(e)
            raise  # used to return entire error details - including stacktrace back to client UI. Best for most use cases

        all_messages = u"\n  ".join(output_messages)
        self.logger.info(u"----------------- Main - Finished -----------------")
        self.logger.info(
            u"status: {}\n  result_value: {}\n  output_message: {}".format(
                status, result_value, all_messages))
        self.siemplify.end(all_messages, result_value, status)

    def execute_action(self, output_messages, successful_entities, failed_entities):
        """
        This abstract method should be implemented to reflect actual behavior to process an entity
        :param output_messages: {list} Mutable list of output messages (str) to form audit trail for this action
        :param successful_entities: {list} List of entity.identifier's, which have been processed successfully
        :param failed_entities: {list} List of entity.identifier's, which have been failed during processing
        :return: {tuple} 1st value - Status of the operation: {int} 0 - success, 1 - failed, 2 - timed out; 2nd value - Success flag: {bool} True - success, False - failure.
        """
        status = EXECUTION_STATE_COMPLETED  # Used to flag back to Siemplify system, the action final status

        for entity in self.siemplify.target_entities:
            self.logger.info(u"Started processing entity: {}".format(entity.identifier))

            if unix_now() >= self.siemplify.execution_deadline_unix_time_ms:
                self.logger.error(u"Timed out. execution deadline ({}) has passed".format(
                    convert_unixtime_to_datetime(self.siemplify.execution_deadline_unix_time_ms)))
                status = EXECUTION_STATE_TIMEDOUT
                break

            try:
                self.execute_action_per_entity(entity, output_messages)

                successful_entities.append(entity.identifier)
                self.logger.info(u"Finished processing entity {0}".format(entity.identifier))

            except Exception as e:
                failed_entities.append(entity.identifier)
                self.logger.error(u"An error occurred on entity {0}".format(entity.identifier))
                self.logger.exception(e)

        if successful_entities:
            output_messages.append(
                u"Successfully processed entities:\n{}".format(
                    u"\n  ".join(successful_entities)))
        else:
            output_messages.append(u"No entities where processed.")

        if failed_entities:
            output_messages.append(
                u"Failed processing entities:{}\n".format(
                    u"\n  ".join(failed_entities)))
            status = EXECUTION_STATE_FAILED

        return status

    def execute_action_per_entity(self, entity, output_messages):
        """
        Abstract method, which should do something per each entity
        :param entity: {AlertInfo} Actual entity instance along with all related information
        :param output_messages: {list} Mutable list of output messages (str) to form audit trail for this action
        """
        raise NotImplementedError()
