import json
import sys

from functools import wraps


def handle_cli_errors(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        try:
            return function(*args, **kwargs)

        except json.JSONDecodeError:
            print(
                "[오류] 저장 파일의 JSON 형식이 손상되었습니다.",
                file=sys.stderr
            )

            print(
                "[힌트] data 폴더의 JSONL 파일을 확인해주세요.",
                file=sys.stderr
            )

            raise SystemExit(1)

        except FileNotFoundError as error:
            print(
                f"[오류] 파일을 찾을 수 없습니다: "
                f"{error.filename}",
                file=sys.stderr
            )

            print(
                "[힌트] 입력한 파일 경로를 확인해주세요.",
                file=sys.stderr
            )

            raise SystemExit(1)

        except PermissionError:
            print(
                "[오류] 파일 접근 권한이 없습니다.",
                file=sys.stderr
            )

            print(
                "[힌트] 파일 및 폴더 권한을 확인해주세요.",
                file=sys.stderr
            )

            raise SystemExit(1)

        except ValueError as error:
            print(
                f"[오류] {error}",
                file=sys.stderr
            )

            print(
                "[힌트] 입력값을 확인하거나 --help를 사용해주세요.",
                file=sys.stderr
            )

            raise SystemExit(1)

        except Exception as error:
            print(
                f"[오류] 처리 중 문제가 발생했습니다: {error}",
                file=sys.stderr
            )

            print(
                "[힌트] 입력값과 데이터 파일을 확인해주세요.",
                file=sys.stderr
            )

            raise SystemExit(1)

    return wrapper