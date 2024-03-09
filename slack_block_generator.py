import urllib3
import json
import logging
import os

class SlackBlockGenerator:
    def __init__(self, webhook_url: str, channel: str, username: str, icon_url: str, logger: logging.Logger):
        self.webhook_url = webhook_url
        self.channel = channel
        self.username = username
        self.icon_url = icon_url
        self.logger = logger
        self.http = urllib3.PoolManager()

    def __new_header(self, header_text: str) -> dict:
        return {
            'type': 'header',
            'text': {
                'type': 'plain_text',
                'text': header_text,
                'emoji': False
            }
        }

    def __new_fields_section(self, fields_section_list: list) -> dict:
        return {
            'type': 'section',
            'fields': fields_section_list
        }

    def __new_text_section(self, text_section_dict: dict) -> dict:
        return {
            'type': 'section',
            'text': text_section_dict
        }

    def __new_field(self, field_text: str) -> dict:
        return {
            'type': 'mrkdwn',
            'text': field_text
        }
    
    def __new_markdown_text_field(self, markdown_text: str) -> dict:
        return {
            'type': 'mrkdwn',
            'text': markdown_text
        }

    def __new_plain_text_field(self, plain_text: str) -> dict:
        return {
            'type': 'plain_text',
            'text': plain_text
        }
    
    def __new_divider(self) -> dict:
        return {
            'type': 'divider',
        }
    
    def __new_context(self, elements_list: list) -> dict:
        return {
            'type': 'context',
            'elements': elements_list
        }

    # def generate_blocks(self, header_text: str, fields: list, text: dict) -> list:
    #     blocks = [
    #         self._new_header(header_text),
    #         self._new_fields_section(fields),
    #         self._new_text_section(text)
    #     ]
    #     return blocks

    def __send_message(self, blocks: list) -> tuple[int, str]:
        data = {
            'channel': self.channel,
            'username': self.username,
            'icon_url': self.icon_url,
            'blocks': blocks
        }

        self.logger.debug("Slack Generated Blocks - " + str(data))

        encoded_data = json.dumps(data).encode('utf-8')
        headers = {'Content-Type': 'application/json'}
        response = self.http.request('POST', self.webhook_url, headers=headers, body=encoded_data)
        
        self.logger.debug("Slack HTTP Response Status- " + str(response.status))
        self.logger.debug("Slack HTTP Response Data - " + str(response.data))

        return (response.status, response.data)
    
    def post_slack_message(self, http_body: dict) -> tuple[int, str]:

        # Iterate through body and build text field for key-value pairs and field section for dictionaries
        slack_blocks = []

        for key, value in http_body.items():

            if 'AWSAccountId' == key:

                slack_blocks.append(
                    self.__new_header(
                        header_text = "AWS Account ID - " + value
                    )
                )

        for key, value in http_body.items():

            self.logger.debug("HTTP Body key - " + str(key) + " : " + str(value))
            text_section_list = []

            if isinstance(value, dict):

                text_section_list.append(
                    self.__new_divider()
                )

                text_section_list.append(
                        self.__new_text_section(
                            text_section_dict = self.__new_markdown_text_field(
                                markdown_text = "*" + (key.split(':')[5]).split('/')[1] + "*"
                            )
                        )
                    )
                
                temp_elements_list = []

                for dict_key, dict_value in value.items():
                    
                    temp_elements_list.append(self.__new_markdown_text_field(
                        markdown_text = dict_key + " - `" + dict_value + "`"
                    ))
                    
                text_section_list.append(
                    self.__new_context(
                        elements_list = temp_elements_list
                    )
                )

                self.logger.debug("(Dict) Text Section - " + str(text_section_list))
            else:

                if 'AWSAccountId' != key:
                    text_section_list.append(
                        self.__new_divider()
                    )
                    text_section_list.append(
                        self.__new_text_section(
                            text_section_dict = self.__new_markdown_text_field(
                                markdown_text = "*" + key + "* - `" + value + "`"
                            )
                        )
                    )

                self.logger.debug("(str) Text Section - " + str(slack_blocks))

            slack_blocks.extend(text_section_list)

            self.logger.debug("Slack Blocks Log - " + str(slack_blocks))

        return self.__send_message(blocks=slack_blocks)