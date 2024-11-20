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
    
    child_account_id = http_body['child_account_id']
    onboarding_id = http_body['onboarding_id']
    account_id = http_body['account_id']

    try:
        logger.debug('Verify Archera Account Integration through Ibexlabs API')
        logger.debug('Event - ' + str(event))

        archera_onboarding_status = archera.verify_onboarding_success(
            child_account_id=child_account_id,
            onboarding_id=onboarding_id,
            customer_aws_account_id=account_id
        )

        logger.debug('Archera Onboarding Status - ' + str(archera_onboarding_status))        
        if archera_onboarding_status:
            return archera_onboarding_status
        else:
            raise Exception('Verify Archera Account Error: Archera Onboarding failed')

    # Handling error response when the account creation failed and there is an exception in calling the API.
    except Exception as e:
        logger.exception('Verify Archera Account Error - ' + str(traceback.print_tb(e.__traceback__)))
        # Respond to HTTP request with failure message
        return {
            'ArcheraAccountCreationStatus': 'ACCOUNT_CREATION_UNVERIFIED'
        }