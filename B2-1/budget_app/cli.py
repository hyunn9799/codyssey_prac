import argparse

from typing import Callable, TypeVar

from .decorators import handle_cli_errors
from .models import Transaction
from .repository import (
    BudgetStore,
    CategoryStore,
    DataStore,
    TransactionRepository,
)
from .service import BudgetService


T = TypeVar("T")


def ask_until_valid(
    message: str,
    validator: Callable[[str], T]
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

    sub = parser.add_subparsers(
        dest="command",
        required=True
    )

    # add
    sub.add_parser(
        "add",
        help="거래 추가"
    )

    # list
    list_parser = sub.add_parser(
        "list",
        help="거래 목록"
    )

    list_parser.add_argument(
        "--limit",
        type=int,
        default=10
    )

    # search
    search = sub.add_parser(
        "search",
        help="거래 검색"
    )

    search.add_argument(
        "--from",
        dest="from_date"
    )

    search.add_argument(
        "--to",
        dest="to_date"
    )

    search.add_argument("--category")
    search.add_argument("--type")
    search.add_argument("--q")
    search.add_argument("--tag")

    # summary
    summary = sub.add_parser(
        "summary",
        help="월별 요약"
    )

    summary.add_argument(
        "--month",
        required=True
    )

    summary.add_argument(
        "--top",
        type=int,
        default=3
    )

    # budget
    budget = sub.add_parser(
        "budget",
        help="예산 관리"
    )

    budget_sub = budget.add_subparsers(
        dest="budget_command",
        required=True
    )

    budget_set = budget_sub.add_parser(
        "set"
    )

    budget_set.add_argument(
        "--month",
        required=True
    )

    budget_set.add_argument(
        "--amount",
        type=int,
        required=True
    )

    # category
    category = sub.add_parser(
        "category",
        help="카테고리 관리"
    )

    category_sub = category.add_subparsers(
        dest="category_command",
        required=True
    )

    category_sub.add_parser("add")
    category_sub.add_parser("list")
    category_sub.add_parser("remove")

    # update
    update = sub.add_parser(
        "update",
        help="거래 수정"
    )

    update.add_argument(
        "--id",
        required=True
    )

    update.add_argument("--date")
    update.add_argument("--type")
    update.add_argument("--category")

    update.add_argument(
        "--amount",
        type=int
    )

    update.add_argument("--memo")
    update.add_argument("--tags")

    # delete
    delete = sub.add_parser(
        "delete",
        help="거래 삭제"
    )

    delete.add_argument(
        "--id",
        required=True
    )

    # import
    import_parser = sub.add_parser(
        "import",
        help="CSV 가져오기"
    )

    import_parser.add_argument(
        "--from",
        dest="source",
        required=True
    )

    # export
    export = sub.add_parser(
        "export",
        help="CSV 내보내기"
    )

    export.add_argument(
        "--out",
        required=True
    )

    export.add_argument("--month")

    export.add_argument(
        "--from",
        dest="from_date"
    )

    export.add_argument(
        "--to",
        dest="to_date"
    )

    return parser


def print_transaction(
    tx: Transaction
) -> None:

    print(
        f"{tx.id} | "
        f"{tx.date} | "
        f"{tx.type} | "
        f"{tx.category} | "
        f"{tx.amount} | "
        f"{tx.memo}"
    )


def run_add(
    service: BudgetService
) -> None:

    date = ask_until_valid(
        "날짜(YYYY-MM-DD): ",
        service.validate_date
    )

    tx_type = ask_until_valid(
        "타입(income/expense): ",
        service.validate_type
    )

    category = ask_until_valid(
        "카테고리: ",
        service.validate_category
    )

    amount = ask_until_valid(
        "금액(양수): ",
        service.validate_amount
    )

    memo = input(
        "메모(선택): "
    ).strip()

    tags_input = input(
        "태그(쉼표로 구분, 없으면 엔터): "
    ).strip()

    tags = [
        tag.strip()
        for tag in tags_input.split(",")
        if tag.strip()
    ]

    tx = service.add_transaction(
        date,
        tx_type,
        category,
        amount,
        memo,
        tags
    )

    print(
        f"[저장 완료] id={tx.id}"
    )


def run_list(
    service: BudgetService,
    limit: int
) -> None:

    found = False

    for tx in service.list_transactions(limit):

        found = True

        print_transaction(tx)

    if not found:
        print(
            "[안내] 저장된 거래가 없습니다."
        )


def run_search(
    service: BudgetService,
    args
) -> None:

    found = False

    for tx in service.search_transactions(
        from_date=args.from_date,
        to_date=args.to_date,
        category=args.category,
        tx_type=args.type,
        query=args.q,
        tag=args.tag
    ):

        found = True

        print_transaction(tx)

    if not found:
        print(
            "[안내] 검색 결과가 없습니다."
        )


def run_category(
    service: BudgetService,
    command: str
) -> None:

    if command == "list":

        for name in service.list_categories():
            print(f"- {name}")

    elif command == "add":

        name = input(
            "카테고리명: "
        ).strip()

        service.add_category(name)

        print(
            f"[저장 완료] category={name}"
        )

    elif command == "remove":

        name = input(
            "삭제할 카테고리명: "
        ).strip()

        service.remove_category(name)

        print(
            f"[삭제 완료] category={name}"
        )


def run_summary(
    service: BudgetService,
    month: str,
    top: int
) -> None:

    result = service.get_summary(
        month,
        top
    )

    if result is None:

        print(
            "[안내] 해당 월의 데이터가 없습니다."
        )

        return

    print(
        f"총 수입: {result['income']}원"
    )

    print(
        f"총 지출: {result['expense']}원"
    )

    print(
        f"잔액: {result['balance']}원"
    )

    if result["budget"] is not None:

        print(
            f"예산: {result['budget']}원 "
            f"(사용률 {result['usage_rate']:.1f}%)"
        )

        if result["exceeded"]:
            print(
                "[경고] 예산을 초과했습니다."
            )

    print(
        f"\n지출 TOP {top}"
    )

    for index, (
        category,
        amount
    ) in enumerate(
        result["top_categories"],
        start=1
    ):

        print(
            f"{index}) "
            f"{category} "
            f"{amount}원"
        )


def run_update(
    service: BudgetService,
    args
) -> None:

    tags = None

    if args.tags is not None:

        tags = [
            tag.strip()
            for tag in args.tags.split(",")
            if tag.strip()
        ]

    tx = service.update_transaction(
        tx_id=args.id,
        date=args.date,
        tx_type=args.type,
        category=args.category,
        amount=args.amount,
        memo=args.memo,
        tags=tags
    )

    print(
        f"[수정 완료] id={tx.id}"
    )


def run_import(
    service: BudgetService,
    source: str
) -> None:

    imported, skipped, errors = (
        service.import_csv(source)
    )

    print(
        f"[완료] "
        f"imported={imported}, "
        f"skipped={skipped}"
    )

    if errors:

        print("\n[건너뜀 내역]")

        for error in errors:
            print(f"- {error}")


@handle_cli_errors
def main() -> None:

    parser = create_parser()
    args = parser.parse_args()

    store = DataStore(
        args.data_dir
    )

    transactions = TransactionRepository(
        store.transactions
    )

    categories = CategoryStore(
        store.categories
    )

    budgets = BudgetStore(
        store.budgets
    )

    service = BudgetService(
        transactions,
        categories,
        budgets
    )

    if args.command == "add":

        run_add(service)

    elif args.command == "list":

        run_list(
            service,
            args.limit
        )

    elif args.command == "search":

        run_search(
            service,
            args
        )

    elif args.command == "summary":

        run_summary(
            service,
            args.month,
            args.top
        )

    elif args.command == "budget":

        service.set_budget(
            args.month,
            args.amount
        )

        print(
            f"[저장 완료] "
            f"{args.month} 예산 "
            f"{args.amount}원"
        )

    elif args.command == "category":

        run_category(
            service,
            args.category_command
        )

    elif args.command == "update":

        run_update(
            service,
            args
        )

    elif args.command == "delete":

        service.delete_transaction(
            args.id
        )

        print(
            f"[삭제 완료] id={args.id}"
        )

    elif args.command == "import":

        run_import(
            service,
            args.source
        )

    elif args.command == "export":

        count = service.export_csv(
            output=args.out,
            month=args.month,
            from_date=args.from_date,
            to_date=args.to_date
        )

        print(
            f"[완료] {args.out} "
            f"({count} records)"
        )