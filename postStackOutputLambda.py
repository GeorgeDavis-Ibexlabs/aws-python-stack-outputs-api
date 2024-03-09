import logging
import os
import base64
import json
from http.client import responses

from slack_block_generator import SlackBlockGenerator

logger = logging.getLogger(__name__)
logger.setLevel(os.environ['LOG_LEVEL'] if 'LOG_LEVEL' in os.environ.keys() else 'INFO')

def lambda_handler(event, context):

    logger.info("Event - " + str(event))

    if 'body' in event:

        body = event['body']

        if event['isBase64Encoded']:
            body = base64.b64decode(body)

        logger.debug("HTTP Status Code - 200")
        logger.info("HTTP Response Body - " + str(body))

        response = {}
        response.update({ 
            "API": { 
                "statusCode": 200,
                "body": responses[200]
            }
        })

        if bool(os.environ["ENABLE_SLACK_INTEGRATION"]):

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
                logger = logger,
            )

            logger.debug("Slack Integration is Enabled. Posting to Slack...")
            slack_http_status = slack.post_slack_message(http_body=json.loads(body))

            response.update({ 
                "SlackAPI": { 
                    "statusCode": slack_http_status[0],
                    "body": slack_http_status[1]
                }
            })

        return response
    
    logger.error("HTTP Error - 500. Message: Invalid HTTP Body.")
    return { "statusCode": 500, "body": "Error" }
