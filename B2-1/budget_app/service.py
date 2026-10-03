from __future__ import annotations
import csv

from dataclasses import replace
from datetime import datetime
from itertools import islice
from pathlib import Path
from typing import Iterator
from uuid import uuid4

from .models import Transaction
from .repository import (
    BudgetStore,
    CategoryStore,
    TransactionRepository,
)


class BudgetService:

    def __init__(
        self,
        transactions: TransactionRepository,
        categories: CategoryStore,
        budgets: BudgetStore
    ):
        self.transactions = transactions
        self.categories = categories
        self.budgets = budgets

    # -------------------------
    # Validation
    # -------------------------

    def validate_date(
        self,
        value: str
    ) -> str:

        try:
            parsed = datetime.strptime(
                value,
                "%Y-%m-%d"
            )

        except ValueError:
            raise ValueError(
                "날짜 형식이 올바르지 않습니다."
            )

        if parsed.strftime("%Y-%m-%d") != value:
            raise ValueError(
                "날짜는 YYYY-MM-DD 형식이어야 합니다."
            )

        return value

    def validate_month(
        self,
        value: str
    ) -> str:

        try:
            parsed = datetime.strptime(
                value,
                "%Y-%m"
            )

        except ValueError:
            raise ValueError(
                "월 형식은 YYYY-MM이어야 합니다."
            )

        if parsed.strftime("%Y-%m") != value:
            raise ValueError(
                "월 형식은 YYYY-MM이어야 합니다."
            )

        return value

    def validate_type(
        self,
        value: str
    ) -> str:

        if value not in (
            "income",
            "expense"
        ):
            raise ValueError(
                "타입은 income 또는 expense만 가능합니다."
            )

        return value

    def validate_amount(
        self,
        value: str
    ) -> int:

        try:
            amount = int(value)

        except ValueError:
            raise ValueError(
                "금액은 정수로 입력해주세요."
            )

        if amount <= 0:
            raise ValueError(
                "금액은 0보다 커야 합니다."
            )

        return amount

    def validate_category(
        self,
        value: str
    ) -> str:

        if not self.categories.exists(value):

            raise ValueError(
                f"등록되지 않은 카테고리입니다: {value}"
            )

        return value

    # -------------------------
    # Add / List
    # -------------------------

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
            raise ValueError(
                "--limit은 1 이상이어야 합니다."
            )

        yield from islice(
            self.transactions.iter_all(
                latest_first=True
            ),
            limit
        )

    # -------------------------
    # Search
    # -------------------------

    def search_transactions(
        self,
        from_date: str | None = None,
        to_date: str | None = None,
        category: str | None = None,
        tx_type: str | None = None,
        query: str | None = None,
        tag: str | None = None
    ) -> Iterator[Transaction]:

        if from_date:
            self.validate_date(from_date)

        if to_date:
            self.validate_date(to_date)

        if (
            from_date
            and to_date
            and from_date > to_date
        ):
            raise ValueError(
                "--from은 --to보다 늦을 수 없습니다."
            )

        if category:
            self.validate_category(category)

        if tx_type:
            self.validate_type(tx_type)

        for tx in self.transactions.iter_all(
            latest_first=True
        ):

            if from_date and tx.date < from_date:
                continue

            if to_date and tx.date > to_date:
                continue

            if category and tx.category != category:
                continue

            if tx_type and tx.type != tx_type:
                continue

            if (
                query
                and query.lower()
                not in tx.memo.lower()
            ):
                continue

            if tag and tag not in tx.tags:
                continue

            yield tx

    # -------------------------
    # Update / Delete
    # -------------------------

    def update_transaction(
        self,
        tx_id: str,
        date: str | None = None,
        tx_type: str | None = None,
        category: str | None = None,
        amount: int | None = None,
        memo: str | None = None,
        tags: list[str] | None = None
    ) -> Transaction:

        transaction = self.transactions.get_by_id(
            tx_id
        )

        if transaction is None:
            raise ValueError(
                f"거래를 찾을 수 없습니다: {tx_id}"
            )

        if date is not None:
            self.validate_date(date)

        if tx_type is not None:
            self.validate_type(tx_type)

        if category is not None:
            self.validate_category(category)

        if amount is not None and amount <= 0:
            raise ValueError(
                "금액은 0보다 커야 합니다."
            )

        updated = replace(
            transaction,
            date=(
                date
                if date is not None
                else transaction.date
            ),
            type=(
                tx_type
                if tx_type is not None
                else transaction.type
            ),
            category=(
                category
                if category is not None
                else transaction.category
            ),
            amount=(
                amount
                if amount is not None
                else transaction.amount
            ),
            memo=(
                memo
                if memo is not None
                else transaction.memo
            ),
            tags=(
                tags
                if tags is not None
                else transaction.tags
            ),
        )

        self.transactions.update(updated)

        return updated

    def delete_transaction(
        self,
        tx_id: str
    ) -> None:

        if not self.transactions.delete(tx_id):

            raise ValueError(
                f"거래를 찾을 수 없습니다: {tx_id}"
            )

    # -------------------------
    # Category
    # -------------------------

    def add_category(
        self,
        name: str
    ) -> None:

        name = name.strip()

        if not name:
            raise ValueError(
                "카테고리 이름을 입력해주세요."
            )

        if self.categories.exists(name):
            raise ValueError(
                "이미 존재하는 카테고리입니다."
            )

        self.categories.add(name)

    def list_categories(
        self
    ) -> Iterator[str]:

        yield from self.categories.iter_names()

    def remove_category(
        self,
        name: str
    ) -> None:

        if not self.categories.exists(name):
            raise ValueError(
                "존재하지 않는 카테고리입니다."
            )

        for tx in self.transactions.iter_all():

            if tx.category == name:
                raise ValueError(
                    "사용 중인 카테고리는 삭제할 수 없습니다."
                )

        self.categories.remove(name)

    # -------------------------
    # Budget
    # -------------------------

    def set_budget(
        self,
        month: str,
        amount: int
    ) -> None:

        self.validate_month(month)

        if amount <= 0:
            raise ValueError(
                "예산은 0보다 커야 합니다."
            )

        self.budgets.set(
            month,
            amount
        )

    # -------------------------
    # Summary
    # -------------------------

    def get_summary(
        self,
        month: str,
        top: int
    ) -> dict | None:

        self.validate_month(month)

        if top <= 0:
            raise ValueError(
                "--top은 1 이상이어야 합니다."
            )

        income = 0
        expense = 0

        category_expenses: dict[str, int] = {}

        found = False

        for tx in self.transactions.iter_all():

            if not tx.date.startswith(month):
                continue

            found = True

            if tx.type == "income":
                income += tx.amount

            else:
                expense += tx.amount

                category_expenses[tx.category] = (
                    category_expenses.get(
                        tx.category,
                        0
                    )
                    + tx.amount
                )

        if not found:
            return None

        top_categories = sorted(
            category_expenses.items(),
            key=lambda item: item[1],
            reverse=True
        )[:top]

        budget = self.budgets.get(month)

        usage_rate = None
        exceeded = False

        if budget is not None:
            usage_rate = expense / budget * 100
            exceeded = expense > budget

        return {
            "income": income,
            "expense": expense,
            "balance": income - expense,
            "top_categories": top_categories,
            "budget": budget,
            "usage_rate": usage_rate,
            "exceeded": exceeded,
        }

    # -------------------------
    # CSV Import
    # -------------------------

    def import_csv(
        self,
        source: str
    ) -> tuple[int, int, list[str]]:

        required_columns = [
            "date",
            "type",
            "category",
            "amount",
            "memo",
            "tags",
        ]

        imported = 0
        skipped = 0
        errors = []

        with Path(source).open(
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            reader = csv.DictReader(file)

            if (
                reader.fieldnames is None
                or any(
                    column not in reader.fieldnames
                    for column in required_columns
                )
            ):
                raise ValueError(
                    "CSV 헤더가 올바르지 않습니다."
                )

            for row_number, row in enumerate(
                reader,
                start=2
            ):

                try:
                    date = self.validate_date(
                        row["date"].strip()
                    )

                    tx_type = self.validate_type(
                        row["type"].strip()
                    )

                    category = self.validate_category(
                        row["category"].strip()
                    )

                    amount = self.validate_amount(
                        row["amount"].strip()
                    )

                    memo = (
                        row.get("memo")
                        or ""
                    ).strip()

                    tags = [
                        tag.strip()
                        for tag in (
                            row.get("tags")
                            or ""
                        ).split(",")
                        if tag.strip()
                    ]

                    self.add_transaction(
                        date,
                        tx_type,
                        category,
                        amount,
                        memo,
                        tags
                    )

                    imported += 1

                except (
                    ValueError,
                    AttributeError
                ) as error:

                    skipped += 1

                    errors.append(
                        f"{row_number}행: {error}"
                    )

        return (
            imported,
            skipped,
            errors
        )

    # -------------------------
    # CSV Export
    # -------------------------

    def export_csv(
        self,
        output: str,
        month: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None
    ) -> int:

        if not (
            month
            or from_date
            or to_date
        ):
            raise ValueError(
                "--month 또는 --from/--to 조건이 필요합니다."
            )

        if month:
            self.validate_month(month)

        if from_date:
            self.validate_date(from_date)

        if to_date:
            self.validate_date(to_date)

        if (
            from_date
            and to_date
            and from_date > to_date
        ):
            raise ValueError(
                "--from은 --to보다 늦을 수 없습니다."
            )

        output_path = Path(output)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        count = 0

        with output_path.open(
            "w",
            encoding="utf-8",
            newline=""
        ) as file:

            fieldnames = [
                "date",
                "type",
                "category",
                "amount",
                "memo",
                "tags",
            ]

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames
            )

            writer.writeheader()

            for tx in self.transactions.iter_all():

                if (
                    month
                    and not tx.date.startswith(month)
                ):
                    continue

                if (
                    from_date
                    and tx.date < from_date
                ):
                    continue

                if (
                    to_date
                    and tx.date > to_date
                ):
                    continue

                writer.writerow({
                    "date": tx.date,
                    "type": tx.type,
                    "category": tx.category,
                    "amount": tx.amount,
                    "memo": tx.memo,
                    "tags": ",".join(tx.tags),
                })

                count += 1

        return count