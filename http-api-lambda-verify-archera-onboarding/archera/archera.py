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
    
    # verify_onboarding_success: Verifies that the Archera Onboarding process was a success. Returns bool.
    def verify_onboarding_success(self, child_account_id: str, onboarding_id: str, customer_aws_account_id: str) -> bool:
        httpBody = {
            'onboarding_id': onboarding_id,
            'account_id': customer_aws_account_id
        }
        try:
            self.logger.debug('Verify Onboarding Request Body: ' + str(httpBody))
            r = self.http.request(
                'POST', self.__get_base_url(account_id=child_account_id) + '/partners/onboarding/aws/verify',
                headers=self.__get_headers(api_key=self.partner_api_key),
                body=json.dumps(httpBody)
            )
            response = json.loads(r.data)
            self.logger.debug('Verify Onboarding Response: ' + str(response))
            if r.status == 200:
                return True
            else:
                self.logger.exception(response)
                if len(response.keys()) == 1:
                    raise Exception('Unknown HTTP error occurred while verifying Archera Onboarding process. ' + str(list(response.keys())[0]).capitalize() + ': ' + str(response[list(response.keys())[0]]).capitalize() + '.')
                elif 'code' in response.keys():
                    raise Exception('Unknown HTTP error occurred while verifying Archera Onboarding process. Error ' + str(response['code']) + ': ' + response['status'] + '.')
                else:
                    raise Exception('Unknown HTTP error occurred while verifying Archera Onboarding process. Error: ' + str(response) + '.')
        except Exception:
            raise