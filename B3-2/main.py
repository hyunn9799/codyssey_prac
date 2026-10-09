import argparse  # CLI 인자 파싱 전용 인터페이스 라이브러리
import os
import sys

from dotenv import load_dotenv

from ai_client import APIError, request_draft
from formatters import format_result, make_prompt
from git_tools import GitError, collect_changes


def parser_factory() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(description="Git 변경 사항으로 커밋 메시지 및 PR 초안 생성")
    subparsers = parser.add_subparsers(dest="command" , required=True)
    for name in ("commit","pr"):
        sub = subparsers.add_parser(name, help=f"{name} 초안 생성")
        sub.add_argument("--model", "-model", default="gpt-4.1-mini", help="API 모델 (기본: gpt-4.1-mini)")
        sub.add_argument("--temperature", "-temperature", type=float, default=0.2, help="0~2 (기본: 0.2)")
        sub.add_argument("--max-tokens", "-max-tokens", type=int, default=650, help="응답 토큰 상한 (기본: 650)")
        sub.add_argument("--safe-mode", "-safe-mode", action="store_true", help="민감값 마스킹, 최대 10파일/200줄 전송")
    return parser


def main(argv: list[str] | None = None) -> int:
    load_dotenv()  # .env 파일을 환경변수로 불러오기
    args = parser_factory().parse_args(argv)
    if not 0 <= args.temperature <= 2:
        print("[ERROR] --temperature는 0~2 사이여야 합니다.", file=sys.stderr)
        return 1
    if args.max_tokens < 32:
        print("[ERROR] --max-tokens는 32 이상이어야 합니다.", file=sys.stderr)
        return 1


    try:
        changes = collect_changes(args.safe_mode)
        if changes is None:
            print("[INFO] 변경 사항이 없습니다. 초안을 생성하지 않고 종료합니다.")
            print("[INFO] API 호출 횟수: 0")
            return 0
        print(f"[INFO] Git status 수집 완료: {changes.file_count}개 파일 변경 감지")
        print(f"[INFO] Git diff 수집 완료: {changes.diff_lines}줄")
        if changes.truncated:
            print("[WARN] 안전/비용 제한에 따라 일부 Git 데이터가 제외되었습니다.")
        if not changes.diff:
            print("[WARN] diff 내용이 없습니다. 미추적 파일의 경우 파일명만 반영됩니다.")
        api_key = os.getenv("AI_API_KEY", "").strip()
        if not api_key:
            print("[ERROR] AI_API_KEY 환경변수가 설정되지 않았습니다.", file=sys.stderr)
            print('[HINT] PowerShell: $env:AI_API_KEY="YOUR_KEY"', file=sys.stderr)
            print('[HINT] Bash: export AI_API_KEY="YOUR_KEY"', file=sys.stderr)
            print("[INFO] API 호출 횟수: 0")
            return 1
        if not args.safe_mode:
            print("[WARN] 일반 모드: 민감정보가 포함된 diff를 외부 API로 보내지 않도록 확인하세요.")
        print(f"[INFO] AI API 요청 중... (model={args.model}, temperature={args.temperature}, max_tokens={args.max_tokens})")
        try:
            draft = request_draft(make_prompt(args.command, changes), api_key, args.model, args.temperature, args.max_tokens)
        finally:
            print("[INFO] API 호출 횟수: 1")
        output, long_title = format_result(args.command, draft)
        print(f"[DONE] {'커밋 메시지' if args.command == 'commit' else 'PR 초안'} 생성 완료")
        if long_title:
            print("[WARN] 커밋 제목이 권장 길이인 50자를 초과했습니다(최대 72자 이내).")
        print("\n" + output)
        return 0
    except (GitError, APIError, ValueError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
    



