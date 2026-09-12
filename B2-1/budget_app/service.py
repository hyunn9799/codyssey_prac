from collections import deque
from datetime import datetime
from typing import Iterator
from uuid import uuid4

from .models import Transaction
from .repository import CategoryStore, TransactionRepository


class BudgetService:
    """입력 검증과 거래 관련 업무 로직을 담당한다."""

    def __init__(
            self,
            transactions: TransactionRepository,
            categories: CategoryStore
    ):
        self.transactions = transactions
        self.categories = categories


    def validate_date(self, value: str) -> str:
        try:
            date = datetime.strptime(value,"%Y-%m-%d")
        except ValueError:
            raise ValueError(
                "날짜 형식이 올바르지 않습니다. 예: 2026-09-12"
            )

        if date.strftime("%Y-%m-%d") != value:
            raise ValueError(
                "날짜 형식은 YYYY-MM-DD 형식이어야 합니다."
            )

        return value




    def validate_amount(self, value: str) -> int:
        try:
            amount = int(value)
        except ValueError:
            raise ValueError("금액은 정수로 입력해주세요.")

        if amount <= 0:
            raise ValueError("금액은 0보다 커야 합니다.")

        return amount

    def validate_category(self, value: str) -> str:
        if not self.categories.exists(value):
            raise ValueError(
                f"등록되지 않은 카테고리입니다: {value}"
            )

        return value



    def add_transaction(
        self,
        date: str,
        tx_type: str,
        category: str,
        amount: int,
        memo: str,
        tags: list[str]
    ) -> Transaction:

        transaction = Transaction(
            id=f"TX-{uuid4().hex[:8].upper()}",
            type=tx_type,
            date=date,
            amount=amount,
            category=category,
            memo=memo,
            tags=tags
        )

        self.transactions.add(transaction)

        return transaction

    def list_transactions(
        self,
        limit: int
    ) -> Iterator[Transaction]:

        if limit <= 0:
            raise ValueError("--limit은 1 이상이어야 합니다.")

        recent = deque(
            self.transactions.iter_all(),
            maxlen=limit
        )

        yield from reversed(recent)