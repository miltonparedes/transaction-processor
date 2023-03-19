import csv
import tempfile
from collections import defaultdict
from dataclasses import asdict
from datetime import datetime
from decimal import Decimal
from typing import List

from aws_lambda_powertools import Logger, Tracer

from .conf import AppConfig as app_conf
from .lib.dataclasses import MonthlySummary, Summary, Transaction, TransactionSummaries
from .ses import SesMailSender

logger = Logger()
tracer = Tracer()


def get_transactions_from_csv_file(file: str) -> List[Transaction]:
    transactions = []

    with open(file, mode="r") as csv_file:
        csv_reader = csv.DictReader(csv_file)

        current_year = datetime.now().year

        for row in csv_reader:
            transaction = Decimal(row["Transaction"])

            transaction_date = datetime.strptime(
                f"{current_year}/{row['Date']}", "%Y/%m/%d"
            )
            transaction_type = "debit" if transaction < 0 else "credit"

            txn = Transaction(
                id=row["Id"],
                amount=abs(transaction),
                date=transaction_date,
                type=transaction_type,
            )
            transactions.append(txn)

    return transactions


def get_csv_file_from_s3(bucket: str, key: str) -> str:
    temp_file = tempfile.NamedTemporaryFile(delete=False)

    app_conf.s3_client().download_file(bucket, key, temp_file.name)

    return temp_file.name


def get_monthly_summary_from_transactions(
    transactions: List[Transaction],
) -> List[MonthlySummary]:
    monthly_summary_data = defaultdict(
        lambda: defaultdict(lambda: {"count": 0, "total": 0})
    )

    for txn in transactions:
        month = txn.date.month
        txn_type = txn.type
        monthly_summary_data[month][txn_type]["count"] += 1
        monthly_summary_data[month][txn_type]["total"] += txn.amount

    monthly_summaries = []

    for month, summary_data in monthly_summary_data.items():
        debit_summary = TransactionSummaries(
            count=summary_data["debit"]["count"], total=summary_data["debit"]["total"]
        )
        credit_summary = TransactionSummaries(
            count=summary_data["credit"]["count"], total=summary_data["credit"]["total"]
        )
        total = debit_summary.total + credit_summary.total
        count = debit_summary.count + credit_summary.count

        monthly_summary = MonthlySummary(
            month=month,
            debit=debit_summary,
            credit=credit_summary,
            total=total,
            count=count,
        )

        monthly_summaries.append(monthly_summary)

    return monthly_summaries


def get_summary_from_monthly_summaries(
    monthly_summaries: List[MonthlySummary],
) -> Summary:
    total_debit_count = 0
    total_debit_amount = 0
    total_credit_count = 0
    total_credit_amount = 0
    total_count = 0
    total_amount = 0

    for monthly_summary in monthly_summaries:
        total_debit_count += monthly_summary.debit.count
        total_debit_amount += monthly_summary.debit.total
        total_credit_count += monthly_summary.credit.count
        total_credit_amount += monthly_summary.credit.total
        total_count += monthly_summary.count
        total_amount += monthly_summary.total

    debit_summary = TransactionSummaries(
        count=total_debit_count, total=total_debit_amount
    )
    credit_summary = TransactionSummaries(
        count=total_credit_count, total=total_credit_amount
    )

    summary = Summary(
        debit=debit_summary,
        credit=credit_summary,
        count=total_count,
        total=total_amount,
        monthly_summaries=monthly_summaries,
    )

    return summary


def store_transactions_in_dynamodb(transactions: List[Transaction]) -> None:
    table = app_conf.dynamo_resource().Table(app_conf.DYNAMO_TABLE)

    with table.batch_writer() as batch:
        for transaction in transactions:
            batch.put_item(
                Item={
                    "id": transaction.id,
                    "amount": transaction.amount,
                    "date": transaction.date.isoformat(),
                    "type": transaction.type,
                }
            )


@tracer.capture_lambda_handler
def handler(event, context):
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"]

    logger.info(f"Processing file from bucket {bucket} with key {key}")

    transactions = get_transactions_from_csv_file(
        file=get_csv_file_from_s3(bucket=bucket, key=key)
    )

    logger.debug(f"Loaded {len(transactions)} transactions from the CSV file")

    monthly_summaries = get_monthly_summary_from_transactions(transactions=transactions)
    summary = get_summary_from_monthly_summaries(monthly_summaries=monthly_summaries)

    logger.debug(f"Calculated summary: {summary}")

    mail_sender = SesMailSender(ses_client=app_conf.ses_client())
    mail_sender.send_templated_email(
        source=app_conf.SOURCE_EMAIL,
        destination_email=app_conf.DESTINATION_EMAIL,
        template_name=app_conf.TEMPLATE_NAME,
        template_data=asdict(summary),
    )
    logger.info("Sent summary email")

    store_transactions_in_dynamodb(transactions=transactions)
    logger.info("Stored transactions in DynamoDB")
