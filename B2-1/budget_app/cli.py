import argparse
from typing import Callable, TypeVar

from .repository import (
    CategoryStore,
    DataStore,
    TransactionRepository,
)

from .service import BudgetService

T = TypeVar("T")

def ask_until_valid(
        message: str,
        validator : Callable[[str] , T]
) -> T:

    while True:
        value = input(message).strip()

        try:
            return validator(value)
        except ValueError as error:
            print(f"[오류] {error}")





def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="budget_app",
        description="콘솔 용돈 기입장"
    )

    parser.add_argument(
        "--data-dir",
        default="./data",
        help="데이터 저장 폴더"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )


    subparsers.add_parser("add", help="거래 추가")
    subparsers.add_parser("list", help="거래 목록")
    subparsers.add_parser("search", help="거래 검색")
    subparsers.add_parser("summary", help="월별 요약")
    subparsers.add_parser("budget", help="예산 관리")
    subparsers.add_parser("category", help="카테고리 관리")
    subparsers.add_parser("update", help="거래 수정")
    subparsers.add_parser("delete", help="거래 삭제")
    subparsers.add_parser("import", help="CSV 가져오기")
    subparsers.add_parser("export", help="CSV 내보내기")

    return parser


def main() -> None:
    parser = create_parser()
    args = parser.parse_args()

    DataStore(args.data_dir)

    print(f"[준비 완료] command={args.command}")