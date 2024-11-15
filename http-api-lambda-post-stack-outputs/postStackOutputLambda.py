import logging
from os import environ
import base64
import json
from http.client import responses

from config_handler.config_handler import ConfigHandler
from jira_handler.jira_handler import JiraHandler
from slack_block_generator.slack_block_generator import SlackBlockGenerator

logger = logging.getLogger(__name__)
logger.setLevel(environ.get('LOG_LEVEL') if 'LOG_LEVEL' in environ.keys() else 'INFO')

from utils.utils import Utils
utilsObj = Utils(logger=logger)

config_handler = ConfigHandler(logger=logger)
config = config_handler.get_combined_config()
logger.debug("Final combined config - " + str(config))

region_name = environ.get("REGION")

if bool(environ.get("ENABLE_JIRA_INTEGRATION")):
    jira = JiraHandler(logger=logger, region_name=region_name, config=config)

def lambda_handler(event, context):

    logger.info("Event - " + str(event))

    if 'body' in event:

        body = event['body']

        if event['isBase64Encoded']:
            body = base64.b64decode(body)

        http_body = json.loads(body)
        logger.debug("HTTP Status Code - 200")
        logger.info("HTTP Response Body - " + str(http_body))

        response = {}
        response.update({ 
            "API": { 
                "statusCode": 200,
                "body": responses[200]
            }
        })

        if bool(environ.get('ENABLE_SLACK_INTEGRATION')):

            # Access environment variables
            slack_webhook_url = utilsObj.get_ssm_parameter(
                parameter_name=environ.get('SLACK_WEBHOOK_URL'),
                region_name=region_name
            )
            slack_channel = environ.get('SLACK_CHANNEL')
            slack_username = environ.get('SLACK_USERNAME')
            slack_icon_url = environ.get('SLACK_ICON_URL')

            slack = SlackBlockGenerator(
                webhook_url = slack_webhook_url,
                channel = slack_channel,
                username = slack_username,
                icon_url = slack_icon_url,
                logger = logger,
            )

            logger.debug("Slack Integration is Enabled. Posting to Slack...")
            slack_http_status = slack.post_slack_message(http_body=http_body)

            response.update({ 
                "SlackAPI": { 
                    "statusCode": slack_http_status[0],
                    "body": slack_http_status[1]
                }
            })

        if bool(environ.get("ENABLE_JIRA_INTEGRATION")):

            logger.debug("JSON Body - " + str(http_body))

            issue = jira.jira_create_issue(
                issue_summary="AWS Account - " + str(http_body["AWSAccountId"]),
                issue_desc=str(http_body)
            )

            create_issue_status = 200 if "-" in str(issue) else 400

            response.update({ 
                "JiraAPI": { 
                    "statusCode": create_issue_status,
                    "body": responses[create_issue_status]
                }
            })

        return response
    
    logger.exception("HTTP Error - 500. Message: Invalid HTTP Body.")
    return { "statusCode": 500, "body": "Error" }
