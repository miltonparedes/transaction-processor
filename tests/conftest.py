import os
import tempfile
from unittest.mock import patch

import pytest


@pytest.fixture
def mock_get_csv_file_from_s3():
    example_csv = "Id,Date,Transaction\n1,01/01,100.0\n2,01/01,-50.0\n3,02/01,30.0"
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        temp_file.write(example_csv)
        temp_file.flush()
        temp_file.seek(0)

    with patch(
        "transaction_processor.app.get_csv_file_from_s3", return_value=temp_file.name
    ) as mock:
        yield mock

    os.remove(temp_file.name)


@pytest.fixture
def mock_send_email():
    with patch("transaction_processor.app.SesMailSender.send_templated_email") as mock:
        yield mock


@pytest.fixture
def mock_store_transactions():
    with patch("transaction_processor.app.store_transactions_in_dynamodb") as mock:
        yield mock


@pytest.fixture
def example_event():
    return {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "example-bucket"},
                    "object": {"key": "example-key"},
                }
            }
        ]
    }
