import json
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
    """저장 파일 경로와 초기화를 담당한다."""

    def __init__(self, data_dir : str= "./data"):
        self.data_dir = Path(data_dir)

        self.transactions = self.data_dir / "transactions.jsonl"
        self.categories = self.data_dir / "categories.jsonl"
        self.budgets = self.data_dir / "budgets.jsonl"

        self._initialize()


    def _initialize(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.transactions.touch(exist_ok=True)
        self.budgets.touch(exist_ok=True)

        if not self.categories.exists() or self.categories.stat().st_size == 0:
            with self.categories.open("w", encoding="utf-8") as file:
                for category in DEFAULT_CATEGORIES:
                    file.write(
                        json.dumps(
                            {"name": category},
                            ensure_ascii=False
                        )
                        + "\n"
                    )


class TransactionRepository:
    """거래 파일의 읽기/쓰기를 담당한다."""

    def __init__(self, path:Path):
        self.path = path

    def add(self, transaction: Transaction) -> None:
        with self.path.open("a",encoding="utf-8") as file:
            file.write(
                json.dumps(
                    transaction.to_dict(),
                    ensure_ascii=False
                )
                + "\n"
            )

    def iter_all(self) -> Iterator[Transaction]:
        """파일 전체를 메모리에 올리지 않고 한 줄씩 반환한다."""

        with self.path.open("r", encoding="utf-8") as file:
            for line in file:
                if not line.strip():
                    continue

                data = json.loads(line)
                yield Transaction.from_dict(data)


class CategoryStore:
    """ 카테고리 조회를 담당한다."""

    def __init__(self,path: Path):
        self.path = path

    def iter_names(self) -> Iterator[str]:
        with self.path.open("r",encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    yield json.loads(line)["name"]

    def exists(self, name:str) -> bool:
        return any(
            category == name
            for category in self.iter_names()
        )
