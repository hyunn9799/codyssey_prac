# AI GitGen — Git 커밋 메시지 / PR 초안 생성기

**Python 3.10+ / CLI / 외부 패키지 설치 불필요 / 필수 과제만 구현 (보너스 제외)**

`git status`, `git diff`에서 변경 파일과 수정 내용을 가져와 OpenAI REST API에 전달하고, **커밋 메시지** 또는 **PR 제목·본문 초안**을 터미널에 출력합니다. 자동 `git commit`, `git push`, PR 생성은 **하지 않습니다**. 생성된 문장은 사람이 검토 후 복사해서 사용합니다.

## 1. 폴더 구조

```text
ai-gitgen/
├── main.py             # CLI 인자, 실행 흐름, 오류 메시지
├── git_tools.py        # Git status/diff 수집, safe-mode
├── ai_client.py        # REST 요청/응답, API 에러 처리
├── formatters.py       # 프롬프트, 제목 길이/PR 형식 후처리
├── tests/
│   └── test_app.py     # 외부 키 없이 실행하는 단위 테스트
├── .gitignore
└── README.md
```

기능을 분리한 이유: **Git 수집**, **API 통신**, **출력 형식**을 독립적으로 수정·검증할 수 있고, 파일 하나가 모든 책임을 떠안지 않게 하기 위해서입니다.

## 2. 설치 및 실행

1. Python 3.10 이상과 Git을 설치합니다.
2. 압축을 풀고 터미널에서 `ai-gitgen` 폴더로 이동합니다.
3. **Git 리포지토리 루트**에서 실행합니다. 이 프로젝트를 독립 리포지토리로 사용할 경우:

```bash
git init
git add .
git commit -m "chore: initial commit"
```

> 최초 커밋에는 Git 사용자 이름/이메일 설정이 필요할 수 있습니다. 첫 커밋 이후 README나 코드 한 줄을 수정하여 `git status`에 변경 사항을 만든 뒤 CLI를 실행하세요. 변경 사항이 없으면 API를 호출하지 않습니다.

**API 키 발급:** [OpenAI API 키 페이지](https://platform.openai.com/api-keys)에서 발급합니다. ChatGPT 유료 구독과 **API 사용 요금은 별개**입니다. 유료 API 크레딧/결제 설정이 필요할 수 있습니다.

**Windows PowerShell:**

```powershell
$env:AI_API_KEY="YOUR_API_KEY"
python main.py commit --safe-mode
python main.py pr --safe-mode
```

**macOS / Linux (Bash):**

```bash
export AI_API_KEY="YOUR_API_KEY"
python main.py commit --safe-mode
python main.py pr --safe-mode
```

API 키는 **환경변수만** 사용합니다. 파일/코드/README에 실제 키를 넣거나 GitHub에 올리지 마세요. 운영체제에서 터미널을 닫으면 해당 세션의 임시 환경변수가 사라질 수 있습니다.

### 명령 옵션

```bash
python main.py commit --model gpt-4.1-mini --temperature 0.2 --max-tokens 650 --safe-mode
python main.py pr     --model gpt-4.1-mini --temperature 0.8 --max-tokens 850 --safe-mode
python main.py commit --help
python main.py pr --help
```

| 옵션 | 기본값 | 의미 |
|---|---|---|
| `--model` (`-model`) | `gpt-4.1-mini` | API 모델명. 예시 모델은 JSON 모드·temperature 옵션과 호환됨 |
| `--temperature` (`-temperature`) | `0.2` | 0~2. 낮으면 비교적 일관되고, 높으면 표현 다양성 증가 |
| `--max-tokens` (`-max-tokens`) | `650` | AI **출력** 토큰 상한. 낮으면 비용/길이는 줄지만 JSON이 잘릴 수 있음 |
| `--safe-mode` (`-safe-mode`) | 꺼짐 | 민감정보 마스킹, 일부 파일 제외, 최대 10개 패치/200줄 |

> 다른 모델은 `temperature`, `max_completion_tokens`, JSON 모드를 지원하지 않을 수 있습니다. 이런 경우 HTTP 400 오류가 표시됩니다. 과제 실행은 기본 모델을 권장합니다.

## 3. 예상 출력 예시

아래는 **구현 형식을 보여 주는 예시이며 실제 API 실행 결과가 아닙니다**. 내용은 수정된 Git 파일에 따라 달라집니다.

### 커밋 메시지

```text
[INFO] Git status 수집 완료: 2개 파일 변경 감지
[INFO] Git diff 수집 완료: 34줄
[INFO] AI API 요청 중... (model=gpt-4.1-mini, temperature=0.2, max_tokens=650)
[INFO] API 호출 횟수: 1
[DONE] 커밋 메시지 생성 완료

--- Commit Message ---
feat: Git 변경 사항 기반 커밋 메시지 생성

- git_tools.py에서 staged/unstaged 변경 수집
- formatters.py에 제목 길이 검증 추가
----------------------
```

### PR 제목 / 본문

```text
[INFO] Git status 수집 완료: 2개 파일 변경 감지
[INFO] Git diff 수집 완료: 34줄
[INFO] AI API 요청 중... (model=gpt-4.1-mini, temperature=0.2, max_tokens=650)
[INFO] API 호출 횟수: 1
[DONE] PR 초안 생성 완료

--- PR Title ---
feat: Git 변경 내용 기반 커밋/PR 초안 생성

--- PR Body ---
## Why
- 변경 내용을 개발자가 일일이 요약하는 작업을 줄이기 위한 초안입니다.

## What
- git status와 git diff를 이용한 변경 사항 수집을 추가했습니다.
- 생성 텍스트에 제목 길이·PR 필수 섹션 검사를 적용했습니다.

## How to Test
- 코드를 수정한 뒤 `python main.py commit --safe-mode`를 실행합니다.
- `python main.py pr --safe-mode` 출력에 3개 필수 섹션이 있는지 확인합니다.
----------------------
```

### 오류/예외

**변경 사항이 없는 경우:**

```text
[INFO] 변경 사항이 없습니다. 초안을 생성하지 않고 종료합니다.
[INFO] API 호출 횟수: 0
```

**변경 사항이 있지만 API 키가 없는 경우:**

```text
[ERROR] AI_API_KEY 환경변수가 설정되지 않았습니다.
[HINT] PowerShell: $env:AI_API_KEY="YOUR_KEY"
[HINT] Bash: export AI_API_KEY="YOUR_KEY"
[INFO] API 호출 횟수: 0
```

**인증 오류 / 네트워크 오류 예시:** `HTTP 401: API Key 인증 실패`, `네트워크 연결/시간 초과 오류` 등을 출력하고 종료 코드 `1`로 종료합니다. `400/403/429`도 구분합니다.

## 4. 어떻게 동작하나요?

```text
CLI commit/pr
   │
   ▼
git status --short       ── 변경 없으면 종료
   │
git diff --cached       ── 스테이징된 변경
+ git diff                ── 아직 스테이징되지 않은 변경
   │
   ▼
선택적으로 --safe-mode 적용 (일부 파일 제외·마스킹·10파일/200줄)
   │
   ▼
커밋/PR 용도의 프롬프트 + Git 데이터 조립
   │
   ▼
AI_API_KEY 확인 → REST POST /v1/chat/completions (1회)
   │
   ▼
JSON 응답 파싱 → 길이/불릿 규칙 후처리 → 구분된 터미널 출력
```

**요청:** `Authorization: Bearer ...`, JSON 본문 `model`, `messages`, `temperature`, `max_completion_tokens`, `response_format=json_object`를 사용합니다.

**응답:** `choices[0].message.content`에 담긴 JSON 문자열을 파싱합니다. `title`, `body` 또는 `why`, `what`, `how_to_test`를 최종 문장으로 변환합니다.

**검증:** 커밋 제목 한 줄·최대 72자(50자 초과 경고), PR 제목 최대 80자, `## Why`·`## What`·`## How to Test` 각 최소 1개 불릿을 후처리로 보장합니다. AI가 형식을 놓치더라도 **API 재호출 없이** 안전한 안내 문구를 채웁니다. 제목은 길면 `…`으로 잘리므로 **문맥이 훼손되지 않았는지 꼭 확인**해야 합니다.

**미추적 새 파일의 한계:** Git의 일반 `git diff`는 아직 `git add`하지 않은 untracked 파일의 **내용**을 보여주지 않습니다. 이 도구는 해당 파일명을 `git status`로 알리지만 내용은 모델로 보내지 않습니다. 새 파일 내용을 분석하려면 먼저 `git add <파일명>`으로 스테이징하세요. 신규 프로젝트는 최초 커밋 후 수정하여 시험하는 방법을 권장합니다.

## 5. 보안 / 비용 / 운영상 주의

- 일반 모드(`--safe-mode` 제외)에서는 `git diff`가 외부 API로 전송됩니다. **실제 프로젝트에서는 `--safe-mode` 사용을 권장**하고, 전송 전에 diff를 직접 확인하세요.
- 안전 모드에서는 `.env`, 개인키(`.pem`, `.key`) 등 일부 패치를 제외하고 `API_KEY=...`, `password=...`, `sk-...`, `Bearer ...`, 이메일 형태를 정규식으로 가립니다. 패치 10개/200줄 상한을 적용합니다. 또한 모드와 무관하게 diff 20,000자 제한을 적용합니다.
- 정규식은 모든 민감정보를 식별하지 못합니다. **안전 모드가 완벽한 익명화/보안 통제를 보장하지는 않습니다.** 특히 영업비밀·개인정보가 포함된 업무 코드는 외부 전송 전에 별도 검토해야 합니다.
- 한 번 실행에 API 요청 1회(변경/키 누락 시 0회)이며 자동 재시도는 없습니다. 출력 토큰 상한을 둬 비용을 통제합니다. 작은 저장소·짧은 diff부터 시험하세요.
- AI는 실제 수행하지 않은 테스트가 통과했다고 말할 수 있습니다. 내용 정확성, 테스트 절차, PR 배경을 사람이 검증해야 합니다.
- 자동 커밋·푸시·PR 생성은 **구현 범위에서 제외**했습니다. 요청에 있는 GitHub 리포지토리 업로드는 개발자가 아래 명령으로 직접 수행합니다.

## 6. 자동 테스트

API 키가 없어도 테스트할 수 있습니다(실제 네트워크/API 호출은 `unittest.mock`으로 대체).

```bash
python -m unittest discover -s tests -v
```

주요 검증: Git 변경 없음, staged/unstaged 패치 수집, 안전 모드 마스킹, 키 누락 시 종료, API 오류 시 종료, 옵션 전달, 커밋 제목 72자 제한, PR 3개 섹션 및 불릿, 프롬프트에 Git 데이터 삽입.

## 7. GitHub 제출 방법

본 프로젝트에서 소스/README를 커밋한 후, GitHub 웹에서 **빈 새 리포지토리**(README 자동 생성 체크 해제)를 만들고 다음 명령을 실행합니다. `YOUR_ID`, `REPO_NAME`은 본인 것으로 변경하세요.

```bash
git branch -M main
git remote add origin https://github.com/YOUR_ID/REPO_NAME.git
git push -u origin main
```

GitHub 인증은 본인 계정의 지원되는 방식(PAT 또는 Git Credential Manager 등)을 사용하세요. **CLI 자체는 `git push`를 실행하지 않습니다.** 평가 증빙을 위해 `git log --oneline`, 리포지토리 파일 목록, 커밋/PR CLI 실행 결과 화면을 준비하세요. PR 실제 생성은 보너스이므로 수행하지 않아도 됩니다.

---

# 평가표 항목별 모범답안 (발표/질의응답용)

> 질문은 첨부 평가표 항목 1~4를 순서대로 반영했습니다. 설명은 이 프로젝트에 **실제로 작성한 코드의 흐름**을 기준으로 합니다. 예시 결과를 실제 API 호출 성공 증빙으로 사용하지 마세요.

## 항목 1 — 필수 동작 시연

**Q1. 프로젝트 루트에서 커밋 생성 명령을 실행하면 출력되는가?**  
A. `python main.py commit --safe-mode`를 실행합니다. `main.py`가 Git 변경 사항을 수집한 다음 API를 한 번 호출하고, 커밋 제목과 불릿 본문을 `--- Commit Message ---` 아래에 출력합니다. 실제 실행은 API 키와 Git 변경 사항이 있어야 합니다.

**Q2. PR 생성 명령을 실행하면 제목·본문이 출력되는가?**  
A. `python main.py pr --safe-mode`를 실행하면 PR 제목과 `Why/What/How to Test` 본문이 구분되어 출력됩니다.

**Q3. API Key가 없으면 어떻게 되는가?**  
A. Git 변경 사항이 있는 상태에서 환경변수 `AI_API_KEY`를 제거하면, 키가 없다는 오류와 설정 방법을 보여주고 API 호출 없이 종료 코드 `1`로 종료합니다.

**Q4. Git 변경 사항이 없으면?**  
A. `git status --short` 결과가 비면 `변경 사항이 없습니다`를 출력하고 종료합니다. API 호출도 하지 않아 비용이 발생하지 않습니다.

**Q5. PR에 필수 섹션 및 불릿이 있는가?**  
A. `formatters.py`가 `## Why`, `## What`, `## How to Test`를 고정된 순서로 출력하고, 각 섹션을 `_bullets()`로 정리합니다. 빈 목록이 오면 검토용 안내 불릿을 넣습니다.

**Q6. temperature 또는 max-tokens를 조정했는가?**  
A. `--temperature 0.2`와 `--temperature 0.8`을 비교 실행할 수 있고, `--max-tokens 350`과 `850`도 시험할 수 있습니다. 값이 실제 REST 요청에 전달되는지는 단위 테스트로 확인했습니다. **출력 차이의 실측은 본인 API 키로 비교 실행해야 합니다.**

**Q7. 길이/형식 규칙을 만족하는가?**  
A. 출력 제목을 한 줄로 정리하고 커밋 72자·PR 80자 이상이면 후처리로 자릅니다. 커밋 50자 초과는 경고하고 PR 3개 섹션에 각각 불릿을 넣습니다. 제목을 자를 때 의미가 깨질 수 있으므로 사용자 검토가 필요합니다.

## 항목 2 — 모듈 및 예외 처리 설계

**Q1. Git 변경 사항 수집과 API 호출을 어떻게 분리했는가?**  
A. `git_tools.py`는 `subprocess.run()`으로 `git status`, `git diff --cached`, `git diff`를 실행하고 `GitChanges`로 반환합니다. `ai_client.py`는 REST API 요청/응답만 담당하므로 Git 동작과 외부 API 동작을 별개로 테스트할 수 있습니다.

**Q2. 프롬프트 구성과 출력 형식은 어떻게 분리했는가?**  
A. `formatters.py`의 `make_prompt()`는 변경 내역과 결과 JSON 구조/규칙을 AI에 제공하고, `format_result()`는 반환된 JSON을 검사·후처리해 사람에게 보여줄 문자열로 바꿉니다. 이렇게 해야 모델 지시문 변경과 화면 형식 변경을 독립적으로 관리할 수 있습니다.

**Q3. API 파라미터를 CLI 옵션으로 변경한 이유와 방식은?**  
A. `argparse`에서 모델/temperature/max-tokens를 입력받아 `request_draft()`에 전달하고 REST 요청 JSON에 넣습니다. 따라서 소스 수정 없이 생성 문장의 다양성과 응답 길이를 시험할 수 있습니다.

**Q4. API Key 누락/네트워크 오류는 어떻게 구현했는가?**  
A. `main.py`는 환경변수를 먼저 확인합니다. `ai_client.py`에서 `HTTPError`로 인증(401), 권한(403), 제한(429), 잘못된 요청(400)을 구분하고, `URLError`와 타임아웃으로 네트워크 오류를 처리합니다. 오류 시 민감한 키는 출력하지 않고 예외를 CLI에 전달하여 오류 메시지와 종료 코드 `1`을 제공합니다.

## 항목 3 — 모델 파라미터·프롬프트·후처리 이해

**Q1. temperature를 높이거나 낮추면?**  
A. 일반적으로 낮은 값(0.2)은 표현이 덜 흔들려 커밋 메시지 같은 일관된 작업에 적합하고, 높은 값(0.8)은 다양한 표현이 나오지만 형식이나 정확성 검토 부담이 늘 수 있습니다. 매번 반드시 달라지거나 항상 같은 문구가 나오는 것은 아닙니다.

**Q2. max_tokens는 어떤 영향을 주며 왜 650인가?**  
A. `max_tokens`는 모델이 생성할 **출력 토큰 상한**입니다. 너무 낮으면 PR의 필수 섹션이 빠지거나 JSON이 중간에서 끊길 수 있습니다. 기본 650은 짧은 커밋과 3섹션 PR에 적당한 시작값으로 설정했지만 실제 필요한 값은 diff와 모델에 따라 다릅니다. 토큰 한도에 걸리면 증설하라는 오류를 보여줍니다.

**Q3. 커밋/PR에 맞는 결과를 위해 프롬프트에 어떤 정보를 주었는가?**  
A. Git 상태의 파일명과 `git diff` 수정 내용, 작업 종류(commit/pr), 제목 길이, JSON 키 구조, 변경 요약과 테스트 방법의 작성 규칙을 전달합니다. 커밋은 짧게 변경 핵심을 쓰고, PR은 왜/무엇을/어떻게 검증할지를 구분해야 하므로 출력 양식을 다르게 지정했습니다.

**Q4. 길이/형식 위반을 재생성 또는 후처리 중 무엇으로 해결했는가?**  
A. **후처리**를 선택했습니다. 모델이 출력한 JSON을 파싱해 제목을 자르고 필수 섹션의 불릿을 보완합니다. API 재요청 없이 매 실행 호출 횟수를 1회로 제한할 수 있고 비용/시간이 예측 가능하기 때문입니다. 잘린 제목과 자동 보완 문구는 최종 검토가 필요합니다.

## 항목 4 — 검토·보안·확장

**Q1. AI 초안을 바로 사용하지 않고 검토해야 하는 이유는?**  
A. AI가 diff를 잘못 요약하거나, 실제로 검증하지 않은 기능에 대해 테스트 완료처럼 기술할 수 있기 때문입니다. 특히 커밋 메시지는 기록으로 남고 PR은 리뷰 판단의 근거가 되므로 변경 사항/원인/테스트 절차를 사람이 확인해야 합니다.

**Q2. git diff에 API Key/개인정보가 포함되면 어떻게 막는가?**  
A. `--safe-mode`에서 `.env`·개인키 등 특정 경로를 제외하고 정규식으로 키/토큰/이메일을 마스킹합니다. 동시에 10개 패치·200줄 상한을 적용합니다. 다만 정규식은 모든 기밀을 잡아내지 못하므로 전송 전 `git diff`를 별도로 검토하고, 민감한 저장소는 외부 전송을 피해야 합니다.

**Q3. 실제 팀 프로젝트에 적용한다면 무엇을 가장 먼저 개선할 것인가?**  
A. **전송 전 diff 미리보기와 사용자 승인 기능**을 가장 먼저 추가하겠습니다. 이유는 팀 소스 코드가 외부 API로 전달될 수 있어 보안 사고 영향이 가장 크기 때문입니다. 그다음 팀별 커밋 prefix/PR 템플릿 설정, 허용 파일 정책, 토큰 사용량/비용 로그 기능을 추가하겠습니다.

## 항목 5 — 보너스

선택 과제이므로 **미구현·미제출**입니다.
