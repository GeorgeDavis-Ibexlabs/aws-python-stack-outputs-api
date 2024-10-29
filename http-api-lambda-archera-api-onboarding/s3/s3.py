import logging
from boto3 import client
from botocore.exceptions import ClientError

class s3CopyFiles:

    # s3CopyFiles Constructor
    # logger: Logger object
    # config: Config Dict
    #
    # Returns: s3CopyFiles object
    # Raises: None
    def __init__(self, logger: logging.Logger, region_name: str):

        self.logger = logger
        self.region_name = region_name
        self.s3_client = client('s3', region_name=self.region_name)

    # check_s3_object_exists: Check if a file exists on an S3 bucket, returns `bool`. 
    def check_s3_object_exists(self, bucket_name: str, object_key: str) -> bool:
            
        try:            
            self.s3_client.head_object(
                Bucket=bucket_name,
                Key=object_key
            )
            return True
        
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                raise

    # s3_put_object: Put S3 object into destination bucket
    def s3_put_object(self, dst_bucket: str, dst_key_prefix: str, dst_key: str, data: str, expiration=3600) -> str:

        # Create the file locally
        with open('/tmp/' + dst_key + '.json', 'w+') as file:
            file.write(data)

        # Upload file to S3
        try:
            self.s3_client.upload_file(
                Filename='/tmp/' + dst_key + '.json',
                Bucket=dst_bucket,
                Key=dst_key_prefix + dst_key
            )
            self.logger.debug(f"File '{dst_key}' uploaded to bucket '{dst_bucket}/{dst_key_prefix}'.")

            # Generate a presigned URL for the uploaded file
            presigned_url = self.s3_client.generate_presigned_url(
                ClientMethod='get_object',
                Params={'Bucket': dst_bucket, 'Key': dst_key_prefix + dst_key},
                ExpiresIn=expiration
            )
            self.logger.debug("Generated presigned URL:", presigned_url)
            return presigned_url

        except Exception as e:
            self.logger.exception(f"Error uploading file or generating URL: {e}")
            return None

