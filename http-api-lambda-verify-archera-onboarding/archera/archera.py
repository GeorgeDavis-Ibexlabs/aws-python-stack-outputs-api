import logging
import urllib3
import json
from os import environ

from utils.utils import Utils

class Archera:

    # Archera Constructor
    # logger: Logger object
    #
    # Returns: Archera object
    # Raises: None
    def __init__(self, logger: logging.Logger, base_url: str, region_name: str):

        self.logger = logger
        self.utils = Utils(logger=self.logger)
        self.http = urllib3.PoolManager()
        self.base_url = base_url
        self.region_name = region_name

        ssm_key_partner_org_account_id = environ.get('SSM_KEY_ARCHERA_PARTNER_ORG_ID') # Archera Partner Account ID
        ssm_key_partner_api_key = environ.get('SSM_KEY_ARCHERA_PARTNER_API_KEY')

        self.partner_account_id = self.utils.get_ssm_parameter(
            parameter_name=ssm_key_partner_org_account_id,
            region_name=region_name
        )        
        self.partner_api_key = self.utils.get_ssm_parameter(
            parameter_name=ssm_key_partner_api_key,
            region_name=self.region_name
        )

    # __get_base_url: Returns str with the customized URL for the Archera REST APIs which includes the base URL and Account ID parameter.
    def __get_base_url(self, account_id: str) -> str:
        return self.base_url + '/org/' + account_id

    # __get_headers: Returns the headers for the Archera REST APIs. Returns dict with the headers.
    def __get_headers(self, api_key: str) -> dict:

        self.logger.debug('Archera API Key: ' + api_key)

        import base64

        # Convert string to bytes
        bytes_str = api_key.encode('utf-8')

        # Encode to Base64
        base64_str = base64.b64encode(bytes_str)

        # Convert bytes back to string for readability
        base64_str = base64_str.decode('utf-8')

        self.logger.debug("Base64 encoded string: " + base64_str)

        return {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + base64_str
        }
    
    # __create_child_account: Creates a new Account under the Archera Partner account using REST APIs. Returns str with the new Account ID.
    def __create_child_account(self, httpHeaders: dict, partner_account_id: str, child_account_name: str) -> str:
        '''
            The HTTP Body can contain the following information
                - company (string, required): Name of the child account
                - labra_subscription_id (string, optional): Labra subscription ID
                - email (string, optional): Email associated with the child account
        '''
        httpBody = {
            'company': child_account_name
        }
        try:
            self.logger.debug('Archera URL: ' + self.__get_base_url(account_id=partner_account_id) + '/partners/onboarding/register_child')
            r = self.http.request(
                'POST', self.__get_base_url(account_id=partner_account_id) + '/partners/onboarding/register_child',
                headers=httpHeaders,
                body=json.dumps(httpBody)
            )
            response = json.loads(r.data)
            self.logger.debug('Create Child Account Response: ' + str(response))
            if r.status == 200:
                return response['org_id']
            else:
                self.logger.exception(response)
                if len(response.keys()) == 1:
                    raise Exception('Unable to initiate Archera Onboarding for child Account ' + str(list(response.keys())[0]).capitalize() + ': ' + str(response[list(response.keys())[0]]).capitalize() + '.')
                elif 'code' in response.keys():
                    raise Exception('Unable to create new Archera Account Error ' + str(response['code']) + ': ' + response['status'] + '.')
                else:
                    raise Exception('Unable to create new Archera Account Error: ' + str(response) + '.')
        except Exception:
            raise

    # __init_child_account_onboarding: Creates a new Account under the Archera Partner account using REST APIs. Returns str with the new Account ID.
    def __init_child_account_onboarding(self, httpHeaders: dict, child_account_id: str) -> str:
        try:
            r = self.http.request(
                'POST', self.__get_base_url(account_id=child_account_id) + '/partners/onboarding/start',
                headers=httpHeaders
            )
            response = json.loads(r.data)
            self.logger.debug('Init Child Account Onboarding Response: ' + str(response))
            if r.status == 200:
                return response['onboarding_id']
            else:
                self.logger.exception(response)
                if len(response.keys()) == 1:
                    raise Exception('Unable to initiate Archera Onboarding for child Account ' + str(list(response.keys())[0]).capitalize() + ': ' + str(response[list(response.keys())[0]]).capitalize() + '.')
                elif 'code' in response.keys():
                    raise Exception('Unable to initiate Archera Onboarding for child Account Error ' + str(response['code']) + ': ' + response['status'] + '.')
                else:
                    raise Exception('Unable to initiate Archera Onboarding for child Account Error: ' + str(response) + '.')
        except Exception:
            raise

    # __get_account_cloudformation_template: Downloads the Archera Account-specific Onboarding template to local filesystem. Returns str.
    def __get_account_cloudformation_template(self, httpHeaders: dict, child_account_id: str) -> str:
        try:
            r = self.http.request(
                'GET', self.__get_base_url(account_id=child_account_id) + '/partners/onboarding/aws/cloudformation_template',
                headers=httpHeaders
            )
            response = json.loads(r.data)
            self.logger.debug('Get Account CloudFormation Template Response: ' + str(response))
            if r.status != 200:
                self.logger.exception(response)
                if len(response.keys()) == 1:
                    raise Exception('Unable to download CloudFormation template for child Account ' + str(list(response.keys())[0]).capitalize() + ': ' + str(response[list(response.keys())[0]]).capitalize() + '.')
                elif 'code' in response.keys():
                    raise Exception('Unable to download CloudFormation template for child Account Error ' + str(response['code']) + ': ' + response['status'] + '.')
                else:
                    raise Exception('Unable to download CloudFormation template for child Account Error: ' + str(response) + '.')
        except Exception:
            raise

        return json.dumps(response['template'])
        
    def create_account(self, customer_account_name: str) -> tuple[bool, dict]:        
        httpHeaders = self.__get_headers(api_key=self.partner_api_key)
        self.logger.debug('HTTP Headers: ' + str(httpHeaders))

        customer_account_id = None
        http_response_data = {}

        self.logger.info('Starting Archera Onboarding')
        customer_account_id = self.__create_child_account(httpHeaders=httpHeaders, partner_account_id=self.partner_account_id, child_account_name=customer_account_name)
        http_response_data.update({'ArcheraChildAccountId': customer_account_id})

        self.logger.debug('Initiating onboarding for Customer Archera Account ID: ' + customer_account_id)
        onboarding_id = self.__init_child_account_onboarding(httpHeaders=httpHeaders, child_account_id=customer_account_id)
        http_response_data.update({'ArcheraOnboardingId': customer_account_id})

        if customer_account_id and onboarding_id:

            self.logger.debug('Downloading the Archera Account-specific Onboarding template to runtime')
            cfn_template_response = self.__get_account_cloudformation_template(httpHeaders=httpHeaders, child_account_id=customer_account_id)

            if cfn_template_response:

                # Setup S3
                s3Copy = s3CopyFiles(
                    logger=self.logger,
                    region_name=self.region_name
                )

                cfn_template_pre_signed_url = s3Copy.s3_put_object(
                    dst_bucket=environ.get('TEMPLATE_BUCKET_NAME'),  
                    dst_key_prefix=environ.get('TEMPLATE_KEY_PREFIX'),      
                    dst_key=customer_account_id,
                    data=cfn_template_response
                )

                if cfn_template_pre_signed_url:                
                    self.logger.info('Archera API Account creation for ' + customer_account_id + ' was successful')
                    http_response_data.update({'ArcheraAccountCreationStatus': 'SUCCESS'})
                    http_response_data.update({'ArcheraCloudFormationTemplateUrl': cfn_template_pre_signed_url})
                    self.logger.info('Finished Archera Account Creation')
                    return True, http_response_data
                else:
                    self.logger.error('Archera API Account creation process for ' + customer_account_id + ' was not successful')
                    http_response_data.update({'ArcheraAccountCreationStatus': 'NEEDS_INVESTIGATION'})
                    return False, http_response_data
            else:
                self.logger.error("Archera's API Account creation failed. Please refer to CloudWatch Logs for a detailed error message.")
                return False, http_response_data