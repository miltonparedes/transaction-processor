import os
import tempfile
from datetime import datetime
from decimal import Decimal

from transaction_processor.app import (
    get_monthly_summary_from_transactions,
    get_summary_from_monthly_summaries,
    get_transactions_from_csv_file,
    handler,
)
from transaction_processor.lib.dataclasses import (
    MonthlySummary,
    Summary,
    Transaction,
    TransactionSummaries,
)


def test_get_transactions_from_csv_file():
    csv_content = "Id,Date,Transaction\n1,01/01,100.0\n2,01/02,-50.0"

    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        temp_file.write(csv_content)
        temp_file.seek(0)

        transactions = get_transactions_from_csv_file(temp_file.name)

    expected_transactions = [
        Transaction(
            id="1",
            amount=Decimal("100.0"),
            date=datetime.strptime(f"{datetime.now().year}/01/01", "%Y/%m/%d"),
            type="credit",
        ),
        Transaction(
            id="2",
            amount=Decimal("50.0"),
            date=datetime.strptime(f"{datetime.now().year}/01/02", "%Y/%m/%d"),
            type="debit",
        ),
    ]

    assert transactions == expected_transactions
    os.remove(temp_file.name)


def test_get_transactions_from_csv_file_empty():
    csv_content = "Id,Date,Transaction\n"

    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        temp_file.write(csv_content)
        temp_file.seek(0)

        transactions = get_transactions_from_csv_file(temp_file.name)

    expected_transactions = []

    assert transactions == expected_transactions
    os.remove(temp_file.name)


def test_get_monthly_summary_from_transactions_empty():
    transactions = []
    expected = []
    result = get_monthly_summary_from_transactions(transactions)
    assert result == expected


def test_get_monthly_summary_from_transactions_single_transaction():
    transactions = [
        Transaction(
            id="1", amount=Decimal("100"), date=datetime(2023, 3, 1), type="credit"
        )
    ]
    expected = [
        MonthlySummary(
            month=3,
            debit=TransactionSummaries(count=0, total=0),
            credit=TransactionSummaries(count=1, total=Decimal("100")),
            total=Decimal("100"),
            count=1,
        )
    ]
    result = get_monthly_summary_from_transactions(transactions)
    assert result == expected


def test_get_monthly_summary_from_transactions_multiple_transactions():
    transactions = [
        Transaction(
            id="1", amount=Decimal("100"), date=datetime(2023, 3, 1), type="credit"
        ),
        Transaction(
            id="2", amount=Decimal("-50"), date=datetime(2023, 3, 2), type="debit"
        ),
        Transaction(
            id="3", amount=Decimal("150"), date=datetime(2023, 4, 1), type="credit"
        ),
        Transaction(
            id="4", amount=Decimal("-25"), date=datetime(2023, 4, 2), type="debit"
        ),
    ]
    expected = [
        MonthlySummary(
            month=3,
            debit=TransactionSummaries(count=1, total=Decimal("-50")),
            credit=TransactionSummaries(count=1, total=Decimal("100")),
            total=Decimal("50"),
            count=2,
        ),
        MonthlySummary(
            month=4,
            debit=TransactionSummaries(count=1, total=Decimal("-25")),
            credit=TransactionSummaries(count=1, total=Decimal("150")),
            total=Decimal("125"),
            count=2,
        ),
    ]
    result = get_monthly_summary_from_transactions(transactions)
    assert result == expected


def test_get_summary_from_monthly_summaries_empty():
    monthly_summaries = []
    expected = Summary(
        debit=TransactionSummaries(count=0, total=0),
        credit=TransactionSummaries(count=0, total=0),
        count=0,
        total=0,
        monthly_summaries=[],
    )
    result = get_summary_from_monthly_summaries(monthly_summaries)
    assert result == expected


def test_get_summary_from_monthly_summaries_single_monthly_summary():
    monthly_summaries = [
        MonthlySummary(
            month=3,
            debit=TransactionSummaries(count=1, total=Decimal("-50")),
            credit=TransactionSummaries(count=1, total=Decimal("100")),
            total=Decimal("50"),
            count=2,
        )
    ]
    expected = Summary(
        debit=TransactionSummaries(count=1, total=Decimal("-50")),
        credit=TransactionSummaries(count=1, total=Decimal("100")),
        count=2,
        total=Decimal("50"),
        monthly_summaries=monthly_summaries,
    )
    result = get_summary_from_monthly_summaries(monthly_summaries)
    assert result == expected


def test_get_summary_from_monthly_summaries_multiple_monthly_summaries():
    monthly_summaries = [
        MonthlySummary(
            month=3,
            debit=TransactionSummaries(count=1, total=Decimal("-50")),
            credit=TransactionSummaries(count=1, total=Decimal("100")),
            total=Decimal("50"),
            count=2,
        ),
        MonthlySummary(
            month=4,
            debit=TransactionSummaries(count=1, total=Decimal("-25")),
            credit=TransactionSummaries(count=1, total=Decimal("150")),
            total=Decimal("125"),
            count=2,
        ),
    ]
    expected = Summary(
        debit=TransactionSummaries(count=2, total=Decimal("-75")),
        credit=TransactionSummaries(count=2, total=Decimal("250")),
        count=4,
        total=Decimal("175"),
        monthly_summaries=monthly_summaries,
    )
    result = get_summary_from_monthly_summaries(monthly_summaries)
    assert result == expected


def test_lambda_handler(
    mock_get_csv_file_from_s3, mock_send_email, mock_store_transactions, example_event
):
    context = {}

    handler(example_event, context)

    mock_get_csv_file_from_s3.assert_called_once()
    mock_send_email.assert_called_once()
    mock_store_transactions.assert_called_once()
