import json

from aws_lambda_powertools import Logger
from botocore.exceptions import ClientError

logger = Logger()


class SesMailSender:
    """Encapsulates functions to send emails with Amazon SES."""

    def __init__(self, ses_client):
        self.ses_client = ses_client

    def send_templated_email(
        self,
        source: str,
        destination_email: str,
        template_name: str,
        template_data: dict,
    ):
        send_args = {
            "Source": source,
            "Destination": {
                "ToAddresses": [
                    destination_email,
                ]
            },
            "Template": template_name,
            "TemplateData": json.dumps(template_data, default=str),
        }
        try:
            response = self.ses_client.send_templated_email(**send_args)
            message_id = response["MessageId"]
            logger.info(
                "Sent templated mail %s from %s to %s.",
                message_id,
                source,
                destination_email,
            )
        except ClientError:
            logger.exception(
                "Couldn't send templated mail from %s to %s.", source, destination_email
            )
            raise
        else:
            return message_id
