from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List


@dataclass
class Transaction:
    id: str
    amount: Decimal
    date: datetime
    type: str  # debit or credit


@dataclass
class TransactionSummaries:
    count: int
    total: Decimal


@dataclass
class MonthlySummary:
    month: str
    debit: TransactionSummaries
    credit: TransactionSummaries
    total: Decimal
    count: int


@dataclass
class Summary:
    debit: TransactionSummaries
    credit: TransactionSummaries
    count: int
    total: Decimal
    monthly_summaries: List[MonthlySummary]
