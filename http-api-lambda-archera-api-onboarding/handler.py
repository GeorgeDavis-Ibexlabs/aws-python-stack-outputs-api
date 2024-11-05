from os import environ
import logging
import cfnresponse
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

# lambda_handler: This script executes as a Custom Resource on the Onboarding CloudFormation stack, dynamically deploying CloudFormation stack from Ibexlabs partners. The script is executed when the stack is created, updated and removed.
def lambda_handler(event, context):
    
    logger.debug('Event - ' + str(event))
    logger.debug('Context - ' + str(context))
    logger.debug('Environment variables - ' + str(environ))

    # Parse HTTP Request Body for request parameters
    customer_account_name = event['Request']
    customer_aws_account_id = event['Requests']('CUSTOMER_AWS_ACCOUNT_ID')

    # Create Stack - The following section gets executed when the deployed stack is created or updated using AWS CloudFormation.
    if event['RequestType'] == 'Create':

        try:
            logger.debug('Create Stack Event - ' + str(event))

            archera_onboarding_status, cfnresponse_data = archera.onboard(
                customer_account_name=customer_account_name + 'c/o Ibexlabs'
            ) # Archera needs `c/o Ibexlabs` suffix at the Partner portal level

            if archera_onboarding_status:
                cfnresponse.send(event, context, cfnresponse.SUCCESS, cfnresponse_data)
            else:
                raise Exception('Create Stack Error: Archera Onboarding failed')

        # Handling `cfnresponse` error response when the stack creation failed and there is an exception in calling the API. 
        except Exception as e:
            logger.exception('Create Stack Error - ' + str(traceback.print_tb(e.__traceback__)))
            cfnresponse.send(event, context, cfnresponse.FAILED, {})

    # Update Stack - The following section gets executed when the deployed parent stack is updated using AWS CloudFormation. It tries to find the child stack and trigger an update.
    if event['RequestType'] == 'Update':

        try:
            logger.debug('Update Stack Event - ' + str(event))

            # TODO: Require an implementation to fetch a list of existing Archera Account IDs
            # archera_update_stack_status = archera.update_stack(account_id=None)

            # if archera_update_stack_status:
            #     # TODO: Send cfnresponse data
            #     cfnresponse.send(event, context, cfnresponse.SUCCESS, {})
            # else:
            #     raise Exception('Update Stack Error: Archera Update failed')
        
            cfnresponse.send(event, context, cfnresponse.SUCCESS, {})

        # Handling `cfnresponse` error response when the stack update failed and there is an exception in calling the API. 
        except Exception as e:
            logger.exception('Update Stack Error - ' + str(traceback.print_tb(e.__traceback__)))
            # TODO: Send cfnresponse data
            cfnresponse.send(event, context, cfnresponse.FAILED, {})