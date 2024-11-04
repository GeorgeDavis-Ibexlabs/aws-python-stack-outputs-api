from boto3 import session
from botocore.exceptions import ClientError
import logging

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
        client = boto3_session.client(
            service_name='secretsmanager',
            region_name=region_name
        )

        try:
            secret = client.get_secret_value(
                SecretId=secret_arn
            )
            if type(secret['SecretString']) == type({}):
                import json
                return json.loads(secret['SecretString'])
            else:
                return secret['SecretString']
        
        except ClientError as e:
            if e.response['Error']['Code'] == 'DecryptionFailureException':
                # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response['Error']['Code'] == 'InternalServiceErrorException':
                # An error occurred on the server side.
                raise e