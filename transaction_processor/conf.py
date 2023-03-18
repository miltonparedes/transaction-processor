import os

import boto3


class AppConfig:
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-2")
    DESTINATION_EMAIL: str = os.getenv("DESTINATION_EMAIL", "hey@milton.sh")
    SOURCE_EMAIL: str = os.getenv("SOURCE_EMAIL", "stori@milton.sh")
    TEMPLATE_NAME: str = os.getenv("TEMPLATE_NAME", "TransactionSummary")
    DYNAMO_TABLE = os.getenv("DYNAMO_TABLE", "Transactions")

    @classmethod
    def s3_client(cls):
        return boto3.client("s3", region_name=cls.AWS_REGION)

    @classmethod
    def dynamo_resource(cls):
        return boto3.resource("dynamodb", region_name=cls.AWS_REGION)

    @classmethod
    def ses_client(cls):
        return boto3.client("ses", region_name=cls.AWS_REGION)
