import logging
import os
import base64
import json

from slack_block_generator import SlackBlockGenerator

logger = logging.getLogger(__name__)
logger.setLevel(os.environ['LOG_LEVEL'] if 'LOG_LEVEL' in os.environ.keys() else 'INFO')

def post_slack_message(http_body: dict):

    # Access environment variables
    slack_webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
    slack_channel = os.environ.get('SLACK_CHANNEL')
    slack_username = os.environ.get('SLACK_USERNAME')
    slack_icon_url = os.environ.get('SLACK_ICON_URL')

    slack = SlackBlockGenerator(
        webhook_url = slack_webhook_url,
        channel = slack_channel,
        username = slack_username,
        icon_url = slack_icon_url,
        logger = logger
    )

    # Iterate through body and build text field for key-value pairs and field section for dictionaries
    slack_blocks = []
    text_section_dict = {}

    for key, value in http_body.items():

        if key == "AWSAccountId":

            slack_blocks.append(
                slack._new_header(
                    header_text = "AWS Account ID - " + value
                )
            )

        else:

            if isinstance(value, dict):

                fields_section_list = []
                for dict_key, dict_value in value.items():
                    fields_section_list.append(
                        slack._new_field(
                            field_text = dict_key + " - " + dict_value
                        )
                    )

                slack_blocks.append(
                    slack._new_fields_section(
                        fields_section_list = fields_section_list
                    )
                )
            else:
                slack_blocks.append(
                    slack._new_plain_text_field(
                        plain_text = key + " - " + value
                    )
                )

    return slack.send_message(blocks=slack_blocks)

def lambda_handler(event, context):

    logger.debug("Event - " + str(event))
    logger.debug("Event Keys - " + str(event.keys()))

    if 'body' in event:

        body = event['body']

        if event['isBase64Encoded']:
            body = base64.b64decode(body)

        logger.debug("HTTP Status Code - 200")
        logger.debug("HTTP Response Body - " + str(body))

        post_slack_message(http_body=json.loads(body))

        return { "statusCode": 200, "body": "Success" }
    
    logger.error("HTTP Error - 500. Message: Invalid HTTP Body.")
    return { "statusCode": 500, "body": "Error" }
