import urllib3
import json
import logging

class SlackBlockGenerator:
    def __init__(self, webhook_url: str, channel: str, username: str, icon_url: str, logger: logging.Logger):
        self.webhook_url = webhook_url
        self.channel = channel
        self.username = username
        self.icon_url = icon_url
        self.logger = logger
        self.http = urllib3.PoolManager()

    def _new_header(self, header_text: str) -> dict:
        return {
            'type': 'header',
            'text': {
                'type': 'plain_text',
                'text': header_text
            }
        }

    def _new_fields_section(self, fields_section_list: list) -> dict:
        return {
            'type': 'section',
            'fields': fields_section_list
        }

    def _new_text_section(self, text_section_dict: dict) -> dict:
        return {
            'type': 'section',
            'text': text_section_dict
        }

    def _new_field(self, field_text: str) -> dict:
        return {
            'type': 'mrkdwn',
            'text': field_text
        }

    def _new_plain_text_field(self, plain_text: str) -> dict:
        return {
            'type': 'plain_text',
            'text': plain_text
        }

    # def generate_blocks(self, header_text: str, fields: list, text: dict) -> list:
    #     blocks = [
    #         self._new_header(header_text),
    #         self._new_fields_section(fields),
    #         self._new_text_section(text)
    #     ]
    #     return blocks

    def send_message(self, blocks: list) -> None:
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
                          
        return response.status