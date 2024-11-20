from os import environ
import logging
import traceback
import boto3

# Setting up the logging level from the environment variable `LOGLEVEL`.
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(environ['LOGLEVEL'] if 'LOGLEVEL' in environ.keys() else 'INFO')

# Setting up logging level specific to `botocore` from the environment variable `BOTOCORE_LOGLEVEL`.
if 'BOTOCORE_LOGLEVEL' in environ.keys():
    if environ['BOTOCORE_LOGLEVEL'] == 'DEBUG':
        logger.info('Setting boto3 logging to DEBUG')
        boto3.set_stream_logger('') # Log everything on boto3 messages to stdout
    else:
        logger.info('Setting boto3 logging to ' + environ['BOTOCORE_LOGLEVEL'])
        boto3.set_stream_logger(level=logging._nameToLevel[environ['BOTOCORE_LOGLEVEL']]) # Log boto3 messages that match BOTOCORE_LOGLEVEL to stdout

# Access environment variables
base_url = environ.get('ARCHERA_BASE_URL')
region_name = environ.get('REGION')
customer_account_name_suffix = environ.get('CUSTOMER_ACCOUNT_NAME_SUFFIX')
environment = environ.get('ENVIRONMENT')

from archera.archera import Archera
archera = Archera(
    logger=logger,
    base_url=base_url,
    region_name=region_name
)

# lambda_handler: This script executes as part of an API to create Archera Accounts using Archera's API. The script is executed when the stack is created, updated and removed.
# Returns the dynamic Archera CloudFormation template in the HTTP API response
def lambda_handler(event, context) -> dict:
    
    logger.debug('Event - ' + str(event))
    logger.debug('Context - ' + str(context))
    logger.debug('Environment variables - ' + str(environ))

    # Parse HTTP Request Body for request parameters
    import json
    http_body = json.loads(event['body'])
    customer_account_name = http_body['CUSTOMER_ACCOUNT_NAME']
    request_type = http_body['REQUEST_TYPE']

    # Get Create Account CloudFormation Template - The following section gets executed when the REQUEST_TYPE is set to CREATE
    if request_type.upper() == 'CREATE':

        try:
            logger.debug('Create Account Integration through CloudFormation Event - ' + str(event))

            archera_onboarding_status, http_response_data = archera.create_account(
                customer_account_name=customer_account_name + ' c/o Ibexlabs'
            ) # Archera needs `c/o Ibexlabs` suffix at the Partner portal level

            logger.debug('Archera Onboarding Status - ' + str(archera_onboarding_status))
            logger.debug('HTTP Response Data - ' + str(http_response_data))
            if archera_onboarding_status:
                # Respond to HTTP request with http_response_data
                http_response_data.update({
                    'ArcheraRequestType': 'CREATE',
                })
                return http_response_data
            else:
                raise Exception('Create Account Error: Archera Onboarding failed')

        # Handling error response when the account creation failed and there is an exception in calling the API.
        except Exception as e:
            logger.exception('Create Account Error - ' + str(traceback.print_tb(e.__traceback__)))
            # Respond to HTTP request with failure message
            return {
                'ArcheraRequestType': 'CREATE',
                'ArcheraAccountCreationStatus': 'ACCOUNT_CREATION_FAILED'
            }

    # Update Account CloudFormation Template - The following section gets executed when the REQUEST_TYPE is set to UPDATE
    if request_type.upper() == 'UPDATE':

        try:
            logger.debug('Update Account Integration through CloudFormation Event - ' + str(event))

            # TODO: Require an implementation to fetch a list of existing Archera Account IDs
            # archera_update_stack_status = archera.update_stack(account_id=None)

            # if archera_update_stack_status:
            #   # TODO: Send HTTP Response Data
            #   pass
            # else:
            #     raise Exception('Update Stack Error: Archera Update failed')
        
            # Respond to HTTP request with some data
            return {
                'ArcheraRequestType': 'UPDATE',
                'ArcheraAccountCreationStatus': 'NOT_IMPLEMENTED'
            }

        # Handling error response when the account update cloudformation API failed and there is an exception in calling the API.
        except Exception as e:
            logger.exception('Update Account Error - ' + str(traceback.print_tb(e.__traceback__)))
            # Respond to HTTP request with failure message
            return {
                'ArcheraRequestType': 'UPDATE',
                'ArcheraAccountCreationStatus': 'NOT_IMPLEMENTED'
            }