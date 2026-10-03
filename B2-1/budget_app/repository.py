from __future__ import annotations
import json
import os
import tempfile
from pathlib import Path
from typing import Iterator

from .models import Transaction


DEFAULT_CATEGORIES = [
    "food",
    "transport",
    "rent",
    "salary",
    "etc",
]


class DataStore:
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)

        self.transactions = self.data_dir / "transactions.jsonl"
        self.categories = self.data_dir / "categories.jsonl"
        self.budgets = self.data_dir / "budgets.jsonl"

        self._initialize()

    def _initialize(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.transactions.touch(exist_ok=True)
        self.budgets.touch(exist_ok=True)

        if (
            not self.categories.exists()
            or self.categories.stat().st_size == 0
        ):
            with self.categories.open("w", encoding="utf-8") as file:
                for category in DEFAULT_CATEGORIES:
                    file.write(
                        json.dumps(
                            {"name": category},
                            ensure_ascii=False
                        ) + "\n"
                    )


def atomic_write_jsonl(
    path: Path,
    rows: Iterator[dict]
) -> None:
    """임시 파일에 먼저 기록한 뒤 원본과 교체한다."""

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            delete=False
        ) as temp:

            temp_path = Path(temp.name)

            for row in rows:
                temp.write(
                    json.dumps(
                        row,
                        ensure_ascii=False
                    ) + "\n"
                )

            temp.flush()
            os.fsync(temp.fileno())

        os.replace(temp_path, path)

    except Exception:
        if temp_path and temp_path.exists():
            temp_path.unlink()

        raise


def iter_lines_reverse(
    path: Path
) -> Iterator[str]:
    """파일 끝에서부터 한 줄씩 읽는다."""

    with path.open("rb") as file:
        file.seek(0, 2)

        position = file.tell()
        buffer = b""

        while position > 0:
            size = min(8192, position)
            position -= size

            file.seek(position)

            buffer = file.read(size) + buffer

            lines = buffer.split(b"\n")
            buffer = lines[0]

            for line in reversed(lines[1:]):
                if line.strip():
                    yield line.decode("utf-8")

        if buffer.strip():
            yield buffer.decode("utf-8")


class TransactionRepository:

    def __init__(self, path: Path):
        self.path = path

    def add(
        self,
        transaction: Transaction
    ) -> None:

        with self.path.open(
            "a",
            encoding="utf-8"
        ) as file:

            file.write(
                json.dumps(
                    transaction.to_dict(),
                    ensure_ascii=False
                ) + "\n"
            )

    def iter_all(
        self,
        latest_first: bool = False
    ) -> Iterator[Transaction]:

        if latest_first:

            for line in iter_lines_reverse(self.path):
                yield Transaction.from_dict(
                    json.loads(line)
                )

            return

        with self.path.open(
            "r",
            encoding="utf-8"
        ) as file:

            for line in file:

                if not line.strip():
                    continue

                yield Transaction.from_dict(
                    json.loads(line)
                )

    def get_by_id(
        self,
        tx_id: str
    ) -> Transaction | None:

        for transaction in self.iter_all():
            if transaction.id == tx_id:
                return transaction

        return None

    def update(
        self,
        updated: Transaction
    ) -> bool:

        found = False

        def rows() -> Iterator[dict]:
            nonlocal found

            for transaction in self.iter_all():

                if transaction.id == updated.id:
                    transaction = updated
                    found = True

                yield transaction.to_dict()

        atomic_write_jsonl(
            self.path,
            rows()
        )

        return found

    def delete(
        self,
        tx_id: str
    ) -> bool:

        found = False

        def rows() -> Iterator[dict]:
            nonlocal found

            for transaction in self.iter_all():

                if transaction.id == tx_id:
                    found = True
                    continue

                yield transaction.to_dict()

        atomic_write_jsonl(
            self.path,
            rows()
        )

        return found


class CategoryStore:

    def __init__(self, path: Path):
        self.path = path

    def iter_names(self) -> Iterator[str]:

        with self.path.open(
            "r",
            encoding="utf-8"
        ) as file:

            for line in file:
                if line.strip():
                    yield json.loads(line)["name"]

    def exists(self, name: str) -> bool:

        return any(
            category == name
            for category in self.iter_names()
        )

    def add(self, name: str) -> None:

        with self.path.open(
            "a",
            encoding="utf-8"
        ) as file:

            file.write(
                json.dumps(
                    {"name": name},
                    ensure_ascii=False
                ) + "\n"
            )

    def remove(self, name: str) -> None:

        def rows() -> Iterator[dict]:

            for category in self.iter_names():

                if category != name:
                    yield {"name": category}

        atomic_write_jsonl(
            self.path,
            rows()
        )


class BudgetStore:

    def __init__(self, path: Path):
        self.path = path

    def set(
        self,
        month: str,
        amount: int
    ) -> None:

        budgets = {}

        with self.path.open(
            "r",
            encoding="utf-8"
        ) as file:

            for line in file:

                if line.strip():
                    data = json.loads(line)

                    budgets[data["month"]] = data["amount"]

        budgets[month] = amount

        def rows() -> Iterator[dict]:

            for saved_month, saved_amount in budgets.items():

                yield {
                    "month": saved_month,
                    "amount": saved_amount
                }

        atomic_write_jsonl(
            self.path,
            rows()
        )

    def get(
        self,
        month: str
    ) -> int | None:

        with self.path.open(
            "r",
            encoding="utf-8"
        ) as file:

            for line in file:

                if not line.strip():
                    continue

                data = json.loads(line)

                if data["month"] == month:
                    return data["amount"]

        return None