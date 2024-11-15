from boto3 import session, client
from botocore.exceptions import ClientError
import logging
import traceback

class Utils:

    # Utils Constructor
    # logger: Logger object
    #
    # Returns: Utils object
    # Raises: None
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    # get_aws_secret: Gets a secret from Ibexlabs AWS Secrets Manager. Returns str with the secret value.
    def get_aws_secret(self, secret_arn: str, region_name: str) -> str:    
        
        # Create a Secrets Manager client
        boto3_session = session.Session()
        secrets_client = boto3_session.client(
            service_name='secretsmanager',
            region_name=region_name
        )

        try:
            self.logger.info('Secret ARN: ' + str(secret_arn))
            secret = secrets_client.get_secret_value(
                SecretId=secret_arn
            )
            if type(secret['SecretString']) == type({}):
                import json
                secret_dict = json.loads(secret['SecretString'])
                self.logger.debug('Secret ARN: ' + str(secret_dict))
                return secret_dict
            else:
                secret_str = secret['SecretString']
                self.logger.debug('Secret value: ' + str(secret_str))
                return secret_str
        
        except ClientError as e:
            if e.response['Error']['Code'] == 'DecryptionFailureException':
                # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
                # Deal with the exception here, and/or rethrow at your discretion.
                self.logger.error('Error: DecryptionFailureException. ' + str(traceback.print_tb(e.__traceback__)))
                raise e
            elif e.response['Error']['Code'] == 'InternalServiceErrorException':
                # An error occurred on the server side.
                self.logger.error('Error: InternalServiceErrorException. ' + str(traceback.print_tb(e.__traceback__)))
                raise e

    # get_ssm_parameter: Gets the value from Ibexlabs AWS SSM Parameter Store. Returns str with the parameter value.
    def get_ssm_parameter(self, parameter_name: str, region_name: str) -> str:

        # Create a SSM client
        ssm_client = client(
            service_name='ssm',
            region_name=region_name
        )

        try:
            self.logger.info('SSM Parameter Name: ' + str(parameter_name))
            parameter_value = ssm_client.get_parameter(
                Name=parameter_name
            )
            if 'Parameter' in parameter_value.keys():
                if 'Value' in parameter_value['Parameter'].keys():
                    return parameter_value['Parameter']['Value']
            else:
                self.logger.error('Error: ParameterNotFound. ')
                raise ssm_client.exceptions.ParameterNotFound

        except Exception as e:
            if e.response['Error']['Code'] == 'ParameterNotFound':
                # AWS SSM Parameter Store can't find the provided parameter key and rethrow the exception
                self.logger.error('Error: ParameterNotFound. ' + str(traceback.print_tb(e.__traceback__)))
                raise e
            elif e.response['Error']['Code'] == 'InternalServerError':
                # An error occurred on the server side.
                self.logger.error('Error: InternalServerError. ' + str(traceback.print_tb(e.__traceback__)))
                raise e