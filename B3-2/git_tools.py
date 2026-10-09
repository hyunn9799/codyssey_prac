"""Git 변경 수집과 외부 전송용 안전 처리."""

from dataclasses import dataclass
import re
import subprocess


class GitError(Exception):
    """Git 명령 실패."""


@dataclass
class GitChanges:
    status: str
    diff: str
    file_count: int
    diff_lines: int
    truncated: bool = False


def _git(*arguments: str) -> str:
    try:
        result = subprocess.run(
            ["git", *arguments], capture_output=True, text=True,
            encoding="utf-8", errors="replace", check=False,
        )
    except FileNotFoundError as exc:
        raise GitError("Git이 설치되지 않았거나 PATH에서 찾을 수 없습니다.") from exc
    if result.returncode != 0:
        detail = result.stderr.strip() or "명령 실행 실패"
        raise GitError(f"git {arguments[0]} 실패: {detail}")
    return result.stdout


# 코드 파일이라도 특정 환경변수/자격증명 파일은 모델로 전송하지 않음.
PRIVATE_PATH = re.compile(r"(?:^|[/\\])(?:\.env(?:\..*)?|id_rsa|id_ed25519|credentials(?:\.json)?|secrets?\.[^/\\]+)$|\.(?:pem|p12|pfx|key)$", re.I)
SECRET_ASSIGNMENT = re.compile(
    r"(?i)(\b(?:api[_-]?key|secret|access[_-]?token|auth[_-]?token|password)\b\s*[:=]\s*)([\"']?)([^\s\"',;]+)"
)
TOKEN_PATTERN = re.compile(r"\bsk-[A-Za-z0-9_-]{10,}\b")
BEARER_PATTERN = re.compile(r"(?i)\bBearer\s+\S+")
EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")


def _redact(text: str) -> str:
    text = SECRET_ASSIGNMENT.sub(r"\1\2[REDACTED]", text)
    text = TOKEN_PATTERN.sub("[REDACTED_TOKEN]", text)
    text = BEARER_PATTERN.sub("Bearer [REDACTED]", text)
    return EMAIL_PATTERN.sub("[REDACTED_EMAIL]", text)


def _private_diff_block(block: str) -> bool:
    header = block.splitlines()[0] if block else ""
    # Git은 파일명 공백 등을 따옴표로 이스케이프할 수 있으므로 보수적으로 검사.
    return bool(PRIVATE_PATH.search(header.replace('"', ""))) or any(
        fragment in header for fragment in ("/.env", "/id_rsa", "/id_ed25519")
    )


def collect_changes(safe_mode: bool = False) -> GitChanges | None:
    """git status + git diff(스테이징/작업 트리)를 모은다.

    새로 생성한 untracked 파일은 git diff 대상이 아니므로 파일명만 전달한다.
    """
    # --short 앞의 공백 2개는 Git 상태 코드의 일부이므로 strip()으로 없애면 안 됨.
    status = _git("status", "--short", "--untracked-files=normal").rstrip("\r\n")
    if not status:
        return None

    staged = _git("diff", "--cached", "--no-ext-diff", "--no-color")
    unstaged = _git("diff", "--no-ext-diff", "--no-color")
    diff = (staged + "\n" + unstaged).strip()
    total_files = len(status.splitlines())
    truncated = False

    if safe_mode:
        # 특정 확장자/파일명 제외, 변경 파일 최대 10개·diff 최대 200줄.
        selected = []
        file_count = 0
        for block in re.split(r"(?=^diff --git )", diff, flags=re.M):
            if not block.strip():
                continue
            if _private_diff_block(block):
                truncated = True
                continue
            if file_count >= 10:
                truncated = True
                break
            file_count += 1
            selected.append(block)
        diff = "".join(selected)
        lines = diff.splitlines()
        if len(lines) > 200:
            truncated = True
            lines = lines[:200]
        diff = _redact("\n".join(lines))
        status_lines = [line for line in status.splitlines() if not PRIVATE_PATH.search(line[3:].strip().strip('"'))]
        if len(status_lines) != len(status.splitlines()) or len(status_lines) > 10:
            truncated = True
        status = _redact("\n".join(status_lines[:10]))

    # 비용 폭주 방지: 안전 모드 여부와 관계없이 프롬프트 입력 크기 제한.
    if len(diff) > 20000:
        diff = diff[:20000]
        truncated = True
    if len(status) > 3000:
        status = status[:3000]
        truncated = True
    return GitChanges(status, diff, total_files, len(diff.splitlines()), truncated)