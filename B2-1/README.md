# Budget App

Python 표준 라이브러리만 사용하여 구현한 **파일 기반 콘솔 용돈 기입장 프로그램**입니다.

거래 추가/조회/검색/수정/삭제뿐 아니라 월별 요약, 카테고리 관리, 월 예산 관리, CSV 가져오기/내보내기 기능을 제공합니다.

내부 데이터는 JSONL 파일에 영구 저장하며, 거래 조회와 검색은 `yield` 기반 Generator를 사용하여 파일 전체를 한 번에 메모리에 올리지 않도록 구현했습니다.

---

## 1. 개발 환경

- Python 3.10 이상
- 외부 라이브러리 사용 없음
- Python 표준 라이브러리만 사용

주요 표준 라이브러리:

- `argparse`
- `dataclasses`
- `json`
- `csv`
- `pathlib`
- `tempfile`
- `os`
- `datetime`
- `uuid`
- `functools`

---

## 2. 프로젝트 구조

```text
money-book/
├── budget_app/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── models.py
│   ├── repository.py
│   ├── service.py
│   └── decorators.py
│
├── data/
│   ├── transactions.jsonl
│   ├── categories.jsonl
│   └── budgets.jsonl
│
└── README.md
```

각 모듈의 책임은 다음과 같습니다.

| 파일 | 책임 |
| --- | --- |
| `models.py` | Transaction 데이터 구조 정의 |
| `repository.py` | JSONL 파일 읽기/쓰기, 수정/삭제 |
| `service.py` | 검증, 검색, 요약, 예산, 카테고리 등 업무 로직 |
| `cli.py` | 명령어 파싱 및 사용자 입력/출력 |
| `decorators.py` | 공통 예외 처리 |
| `__main__.py` | `python -m budget_app` 실행 진입점 |

모델, 저장소, 서비스, CLI를 분리하여 각 코드가 하나의 책임에 집중하도록 구성했습니다.

---

## 3. 실행 방법

프로젝트 루트에서 실행합니다.

```bash
python -m budget_app --help
```

기본 데이터 저장 위치는 다음과 같습니다.

```text
./data
```

다른 데이터 폴더를 사용하려면 `--data-dir` 옵션을 사용할 수 있습니다.

```bash
python -m budget_app --data-dir ./mydata list
```

---

# 4. 주요 기능

## 4.1 거래 추가

```bash
python -m budget_app add
```

실행하면 대화형으로 거래 정보를 입력합니다.

예시:

```text
날짜(YYYY-MM-DD): 2026-10-03
타입(income/expense): expense
카테고리: food
금액(양수): 15000
메모(선택): 점심
태그(쉼표로 구분, 없으면 엔터): meal,work
[저장 완료] id=TX-AB12CD34
```

입력 검증 항목:

- 날짜 형식: `YYYY-MM-DD`
- type: `income` 또는 `expense`
- 금액: 0보다 큰 정수
- category: 등록되어 있는 카테고리만 허용

거래 ID는 자동으로 생성됩니다.

---

## 4.2 거래 목록

```bash
python -m budget_app list
```

기본적으로 최근 거래 10건을 출력합니다.

```bash
python -m budget_app list --limit 3
```

예시:

```text
TX-AB12CD34 | 2026-10-03 | expense | food | 15000 | 점심
TX-BC23DE45 | 2026-10-02 | income | salary | 3000000 | 월급
TX-CD34EF56 | 2026-10-01 | expense | transport | 1500 | 버스
```

목록 조회는 파일 전체를 리스트로 변환하지 않고 Generator 기반으로 처리합니다.

---

# 5. 거래 검색

다음 조건을 지원합니다.

- 기간
- 카테고리
- 거래 타입
- 메모 키워드
- 태그

## 기간 검색

```bash
python -m budget_app search \
  --from 2026-10-01 \
  --to 2026-10-31
```

## 카테고리 검색

```bash
python -m budget_app search --category food
```

## 거래 타입 검색

```bash
python -m budget_app search --type expense
```

## 메모 검색

```bash
python -m budget_app search --q 점심
```

## 태그 검색

```bash
python -m budget_app search --tag meal
```

여러 조건을 동시에 사용할 수도 있습니다.

```bash
python -m budget_app search \
  --type expense \
  --category food \
  --tag meal
```

검색 결과는 최신순으로 출력됩니다.

---

# 6. 월별 요약

```bash
python -m budget_app summary \
  --month 2026-10 \
  --top 3
```

출력 예시:

```text
총 수입: 3000000원
총 지출: 215000원
잔액: 2785000원
예산: 500000원 (사용률 43.0%)

지출 TOP 3
1) rent 150000원
2) food 45000원
3) transport 20000원
```

월별 요약에서는 다음 정보를 제공합니다.

- 총 수입
- 총 지출
- 잔액
- 카테고리별 지출 TOP N
- 설정된 월 예산
- 예산 사용률
- 예산 초과 여부

해당 월의 거래가 없으면 다음 메시지를 출력합니다.

```text
[안내] 해당 월의 데이터가 없습니다.
```

---

# 7. 월 예산 관리

월별 예산을 설정할 수 있습니다.

```bash
python -m budget_app budget set \
  --month 2026-10 \
  --amount 500000
```

출력:

```text
[저장 완료] 2026-10 예산 500000원
```

예산은 `budgets.jsonl` 파일에 영구 저장됩니다.

Summary 실행 시 예산이 존재하면 사용률을 계산합니다.

```text
사용률 = 총 지출 / 예산 × 100
```

예산을 초과한 경우:

```text
[경고] 예산을 초과했습니다.
```

메시지를 출력합니다.

---

# 8. 카테고리 관리

## 카테고리 목록

```bash
python -m budget_app category list
```

예시:

```text
- food
- transport
- rent
- salary
- etc
```

초기 실행 시 기본 카테고리가 자동 생성됩니다.

기본 카테고리:

```text
food
transport
rent
salary
etc
```

---

## 카테고리 추가

```bash
python -m budget_app category add
```

예시:

```text
카테고리명: game
[저장 완료] category=game
```

---

## 카테고리 삭제

```bash
python -m budget_app category remove
```

예시:

```text
삭제할 카테고리명: game
[삭제 완료] category=game
```

거래에서 현재 사용 중인 카테고리는 삭제할 수 없습니다.

예:

```text
[오류] 사용 중인 카테고리는 삭제할 수 없습니다.
[힌트] 입력값을 확인하거나 --help를 사용해주세요.
```

데이터 무결성을 위해 거래가 존재하는 카테고리의 삭제를 차단합니다.

---

# 9. 거래 수정

이 프로젝트에서는 **옵션 기반 update 방식**을 사용합니다.

기본 형식:

```bash
python -m budget_app update \
  --id <거래ID> \
  [수정할 옵션]
```

예:

```bash
python -m budget_app update \
  --id TX-AB12CD34 \
  --amount 20000
```

여러 필드를 동시에 수정할 수도 있습니다.

```bash
python -m budget_app update \
  --id TX-AB12CD34 \
  --category transport \
  --amount 30000 \
  --memo "택시"
```

지원 옵션:

```text
--date
--type
--category
--amount
--memo
--tags
```

성공:

```text
[수정 완료] id=TX-AB12CD34
```

존재하지 않는 ID:

```text
[오류] 거래를 찾을 수 없습니다: TX-NOTFOUND
[힌트] 입력값을 확인하거나 --help를 사용해주세요.
```

---

# 10. 거래 삭제

```bash
python -m budget_app delete \
  --id TX-AB12CD34
```

성공:

```text
[삭제 완료] id=TX-AB12CD34
```

없는 ID를 삭제하려 하면 오류 메시지를 출력하고 비정상 종료합니다.

---

# 11. CSV Export

내부 저장은 JSONL을 사용하지만 외부 데이터 교환을 위해 CSV 내보내기를 지원합니다.

## 월 기준 Export

```bash
python -m budget_app export \
  --out export.csv \
  --month 2026-10
```

예:

```text
[완료] export.csv (12 records)
```

## 기간 기준 Export

```bash
python -m budget_app export \
  --out export.csv \
  --from 2026-10-01 \
  --to 2026-10-31
```

Export는 조건 없이 실행할 수 없습니다.

```bash
python -m budget_app export --out export.csv
```

오류:

```text
[오류] --month 또는 --from/--to 조건이 필요합니다.
```

---

# 12. CSV Import

```bash
python -m budget_app import \
  --from import.csv
```

정상 데이터:

```text
[완료] imported=5, skipped=0
```

일부 잘못된 데이터가 존재하는 경우:

```text
[완료] imported=3, skipped=2

[건너뜀 내역]
- 4행: 날짜 형식이 올바르지 않습니다.
- 7행: 금액은 정수로 입력해주세요.
```

Import는 **부분 성공 방식**을 사용합니다.

한 행의 오류 때문에 정상적인 모든 거래를 취소하지 않고:

1. 정상 행은 저장
2. 잘못된 행은 건너뜀
3. 성공/실패 개수 출력
4. 실패한 행 번호와 원인을 출력

하는 방식으로 처리합니다.

이를 통해 사용자는 어떤 데이터가 실제로 반영되었는지 확인할 수 있습니다.

---

# 13. Import / Export CSV 스키마

CSV는 다음 형식을 사용합니다.

- UTF-8
- 헤더 포함

| column | required | 설명 |
| --- | --- | --- |
| `date` | Y | `YYYY-MM-DD` |
| `type` | Y | `income` / `expense` |
| `category` | Y | 등록된 카테고리 |
| `amount` | Y | 양수 정수 |
| `memo` | N | 문자열 |
| `tags` | N | 쉼표(`,`) 구분 문자열 |

예시:

```csv
date,type,category,amount,memo,tags
2026-10-01,expense,food,15000,점심,"meal,work"
2026-10-02,income,salary,3000000,월급,salary
```

---

# 14. 데이터 저장

프로그램 데이터는 기본적으로 다음 위치에 저장됩니다.

```text
./data
```

총 3개의 JSONL 파일을 사용합니다.

```text
data/
├── transactions.jsonl
├── categories.jsonl
└── budgets.jsonl
```

각 파일의 역할:

| 파일 | 저장 내용 |
| --- | --- |
| `transactions.jsonl` | 거래 내역 |
| `categories.jsonl` | 카테고리 |
| `budgets.jsonl` | 월별 예산 |

따라서 프로그램을 종료해도 데이터가 파일에 남아 있으며 다음 실행 시 다시 사용할 수 있습니다.

---

# 15. JSONL 저장 형식

JSONL은 한 줄에 하나의 JSON 객체를 저장합니다.

예:

```json
{"id":"TX-AB12CD34","type":"expense","date":"2026-10-03","amount":15000,"category":"food","memo":"점심","tags":["meal","work"]}
{"id":"TX-BC23DE45","type":"income","date":"2026-10-02","amount":3000000,"category":"salary","memo":"월급","tags":[]}
```

일반 JSON 배열 대신 JSONL을 선택한 이유는 데이터를 한 줄씩 순차 처리하기 쉽기 때문입니다.

---

# 16. JSONL과 CSV 비교

## JSONL 장점

- 한 줄에 하나의 거래 저장
- Generator를 사용한 스트리밍 처리가 쉬움
- JSON 구조를 그대로 사용 가능
- `tags` 같은 리스트 타입을 자연스럽게 저장 가능

## JSONL 단점

- Excel 등에서 바로 열어보기 불편함
- 일반 사용자가 직접 편집하기에는 CSV보다 불편함

## CSV 장점

- Excel 등에서 쉽게 열 수 있음
- 다른 프로그램과 데이터 교환이 쉬움
- 사람이 직접 확인하기 쉬움

## CSV 단점

- 리스트와 같은 복합 데이터 표현이 불편함
- 쉼표, 따옴표 등의 escaping 처리가 필요함

따라서 이 프로젝트에서는:

```text
내부 저장 → JSONL
외부 데이터 교환 → CSV
```

방식을 선택했습니다.

---

# 17. Generator 기반 스트리밍

거래 파일 전체를 한 번에 메모리에 올리지 않습니다.

Repository에서는 다음과 같이 한 거래씩 반환합니다.

```python
def iter_all(self) -> Iterator[Transaction]:
    with self.path.open("r", encoding="utf-8") as file:
        for line in file:
            yield Transaction.from_dict(
                json.loads(line)
            )
```

일반적인 방식:

```text
파일 전체 읽기
↓
모든 데이터를 list에 저장
↓
처리
```

Generator 방식:

```text
한 줄 읽기
↓
Transaction 한 건 생성
↓
yield
↓
처리
↓
다음 줄 읽기
```

따라서 거래가 많아져도 전체 거래를 동시에 메모리에 보관하지 않아도 됩니다.

Generator의 주된 장점은 **속도가 아니라 메모리 효율**입니다.

---

# 18. 검색 스트리밍

검색도 결과 전체를 리스트에 담지 않고 조건을 통과한 거래만 `yield`합니다.

동작 흐름:

```text
JSONL 파일
↓
Transaction 한 건 읽기
↓
날짜 조건 확인
↓
카테고리 조건 확인
↓
type 확인
↓
메모/태그 확인
↓
조건을 모두 통과하면 yield
↓
CLI에서 바로 출력
```

이를 통해 대량 데이터에서도 불필요한 결과 리스트 생성을 줄였습니다.

---

# 19. 안전한 Update / Delete

JSONL 파일에서 특정 한 줄만 직접 수정하기는 어렵기 때문에 update/delete는 파일 재작성 방식으로 처리합니다.

하지만 원본 파일을 바로 덮어쓰지 않습니다.

동작 과정:

```text
기존 transactions.jsonl
        ↓
임시 파일 생성
        ↓
수정/삭제 결과 기록
        ↓
flush()
        ↓
fsync()
        ↓
모든 기록 성공
        ↓
os.replace()
        ↓
원본 파일 교체
```

핵심 코드:

```python
temp.flush()
os.fsync(temp.fileno())

os.replace(temp_path, path)
```

중간에 오류가 발생하면 기존 원본 파일은 그대로 유지됩니다.

이 방식으로 파일 재작성 도중 데이터가 중간 상태로 손상될 가능성을 줄였습니다.

---

# 20. 상태 데이터의 책임 분리

이 프로젝트에서는 각 클래스가 담당하는 책임을 구분했습니다.

## Transaction

```text
거래 데이터 자체의 구조
```

예:

```python
@dataclass
class Transaction:
    id: str
    type: str
    date: str
    amount: int
    category: str
    memo: str
    tags: list[str]
```

## TransactionRepository

```text
거래 데이터를 어떻게 저장하고 읽을지 담당
```

예:

- JSONL 저장
- 거래 조회
- Update
- Delete

## BudgetService

```text
거래 데이터를 가지고 어떤 업무를 수행할지 담당
```

예:

- 날짜 검증
- 금액 검증
- 검색
- 월별 요약
- 카테고리 사용 여부 확인
- 예산 사용률 계산

이처럼:

```text
데이터 구조
저장 방법
업무 규칙
사용자 입출력
```

을 서로 분리했습니다.

---

# 21. Decorator

CLI에서 발생하는 공통 예외 처리는 Decorator로 분리했습니다.

```python
@handle_cli_errors
def main():
    ...
```

처리하는 대표적인 오류:

- 잘못된 입력
- 파일 없음
- 파일 접근 권한 문제
- JSON 파일 손상
- 예상하지 못한 오류

각 명령에서 동일한 `try/except`를 반복하지 않고 Decorator에서 공통으로 처리합니다.

이를 통해 실제 명령 코드에서는 업무 로직에 집중할 수 있습니다.

---

# 22. 오류 처리

오류 발생 시 Python Stack Trace를 사용자에게 그대로 출력하지 않습니다.

예:

```text
[오류] 거래를 찾을 수 없습니다: TX-AAAA
[힌트] 입력값을 확인하거나 --help를 사용해주세요.
```

파일이 존재하지 않는 경우:

```text
[오류] 파일을 찾을 수 없습니다: import.csv
[힌트] 입력한 파일 경로를 확인해주세요.
```

JSONL 데이터가 손상된 경우:

```text
[오류] 저장 파일의 JSON 형식이 손상되었습니다.
[힌트] data 폴더의 JSONL 파일을 확인해주세요.
```

사용자가 오류 원인과 해결 방법을 바로 알 수 있도록 구성했습니다.

---

# 23. 종료 코드

프로그램이 정상적으로 실행된 경우:

```text
exit code = 0
```

오류가 발생한 경우:

```text
exit code = 1
```

Linux/macOS에서 확인:

```bash
echo $?
```

PowerShell에서 확인:

```powershell
$LASTEXITCODE
```

예:

```bash
python -m budget_app delete --id WRONG-ID
```

실행 후:

```powershell
$LASTEXITCODE
```

결과:

```text
1
```

---

# 24. 타입 힌트

함수와 클래스에 타입 힌트를 적용했습니다.

예:

```python
def get_by_id(
    self,
    tx_id: str
) -> Transaction | None:
```

이 코드를 통해:

- 입력값은 `str`
- 반환값은 `Transaction` 또는 `None`

이라는 함수의 계약을 코드만 보고 확인할 수 있습니다.

또 다른 예:

```python
def list_transactions(
    self,
    limit: int
) -> Iterator[Transaction]:
```

`limit`은 정수이며 Generator가 `Transaction` 객체를 반환한다는 점을 알 수 있습니다.

타입 힌트의 장점:

- 함수 입력/출력 구조 확인이 쉬움
- IDE 자동완성 개선
- 코드 가독성 향상
- 잘못된 타입 사용을 조기에 발견하기 쉬움

단, Python의 타입 힌트는 기본적으로 런타임에서 타입을 강제로 제한하는 기능은 아닙니다.

---

# 25. 10만 건 이상의 데이터가 있을 경우

Generator를 사용하면 모든 거래를 한꺼번에 메모리에 올리지 않으므로 메모리 사용량은 줄일 수 있습니다.

하지만 현재 JSONL 구조에서는 다음 작업이 파일 전체 순회를 필요로 합니다.

```text
search
summary
update
delete
```

따라서 데이터가 많아질수록 디스크 I/O가 주요 병목이 됩니다.

현재 구조의 대략적인 특성:

```text
search   → O(N)
summary  → O(N)
update   → O(N)
delete   → O(N)
```

거래가 매우 많아진다면 다음과 같은 개선이 가능합니다.

### 1단계

월별 JSONL 파일 분리

```text
transactions-2026-09.jsonl
transactions-2026-10.jsonl
transactions-2026-11.jsonl
```

월별 검색 시 필요한 파일만 읽을 수 있습니다.

### 2단계

별도의 인덱스 구조 추가

예:

- 날짜
- 카테고리
- ID

### 3단계

SQLite와 같은 데이터베이스로 변경

예:

```text
Transaction Table
+
date index
+
category index
+
id primary key
```

더 큰 규모에서는 JSONL보다 데이터베이스가 검색, 수정, 삭제에 적합합니다.

---

# 26. Import 데이터 오류 정책

CSV Import 파일에 일부 잘못된 행이 포함될 수 있습니다.

이 프로젝트에서는 **부분 성공 + 오류 리포트 방식**을 사용합니다.

예:

```text
100개 행

98개 정상
2개 오류
```

결과:

```text
[완료] imported=98, skipped=2

[건너뜀 내역]
- 14행: 날짜 형식이 올바르지 않습니다.
- 27행: 금액은 정수로 입력해주세요.
```

한 행의 오류 때문에 정상 데이터까지 모두 취소하지 않는 이유는 정상 데이터까지 다시 입력해야 하는 불편을 줄이기 위해서입니다.

대신 어떤 행이 저장되지 않았는지 명확하게 알려주어 사용자가 결과를 확인할 수 있도록 했습니다.

---

# 27. 주요 설계 선택 요약

## JSONL을 선택한 이유

```text
한 줄 = 한 거래
↓
Generator 스트리밍 처리에 적합
↓
tags 같은 리스트 데이터 표현 가능
```

## Service를 분리한 이유

```text
Repository
→ 데이터를 저장하는 방법

Service
→ 데이터를 사용하는 업무 규칙
```

저장 방식과 업무 로직을 서로 분리하기 위해 사용했습니다.

## Decorator를 사용한 이유

```text
여러 명령에서 반복되는 예외 처리
↓
Decorator로 분리
↓
중복 감소
↓
기능 코드가 업무 로직에 집중
```

## 임시 파일을 사용하는 이유

```text
원본 직접 수정
→ 중간 오류 시 파일 손상 위험

임시 파일 작성
→ 작성 성공 후 os.replace()
→ 기존 원본 보호
```

---

# 28. 주요 명령어 한눈에 보기

```bash
# 도움말
python -m budget_app --help

# 거래 추가
python -m budget_app add

# 최근 거래 5개
python -m budget_app list --limit 5

# 검색
python -m budget_app search --category food
python -m budget_app search --type expense
python -m budget_app search --q 점심
python -m budget_app search --tag meal
python -m budget_app search --from 2026-10-01 --to 2026-10-31

# 카테고리
python -m budget_app category list
python -m budget_app category add
python -m budget_app category remove

# 예산
python -m budget_app budget set --month 2026-10 --amount 500000

# 월별 요약
python -m budget_app summary --month 2026-10 --top 3

# 거래 수정
python -m budget_app update \
  --id TX-AB12CD34 \
  --amount 20000

# 거래 삭제
python -m budget_app delete \
  --id TX-AB12CD34

# CSV Export
python -m budget_app export \
  --out export.csv \
  --month 2026-10

# 기간 CSV Export
python -m budget_app export \
  --out export.csv \
  --from 2026-10-01 \
  --to 2026-10-31

# CSV Import
python -m budget_app import \
  --from import.csv
```

---

# 29. 기능 체크리스트

- [x] 거래 추가
- [x] 거래 목록
- [x] `--limit`
- [x] 최신순 출력
- [x] 거래 검색
- [x] 날짜 검색
- [x] 카테고리 검색
- [x] type 검색
- [x] 메모 검색
- [x] tag 검색
- [x] 월별 요약
- [x] 총 수입
- [x] 총 지출
- [x] 잔액
- [x] 카테고리별 지출 TOP N
- [x] 월 예산 설정
- [x] 예산 사용률
- [x] 예산 초과 경고
- [x] 카테고리 추가
- [x] 카테고리 목록
- [x] 카테고리 삭제
- [x] 사용 중 카테고리 삭제 방지
- [x] 거래 수정
- [x] 거래 삭제
- [x] 없는 ID 처리
- [x] CSV Import
- [x] CSV Export
- [x] Import 부분 성공
- [x] 오류 행 리포트
- [x] Generator
- [x] Decorator
- [x] Type Hint
- [x] JSONL 영구 저장
- [x] 3개 저장 파일
- [x] 임시 파일 기반 안전한 수정/삭제
- [x] 오류 Stack Trace 차단
- [x] 오류 종료 코드 1
- [x] Python 표준 라이브러리만 사용

---

# 30. 학습 포인트

이 프로젝트를 통해 다음 내용을 학습했습니다.

- Python 파일 입출력
- JSONL 데이터 저장
- CSV 데이터 교환
- CRUD 구현
- CLI 프로그램 설계
- `argparse`
- `dataclass`
- Generator와 `yield`
- Decorator
- Type Hint
- 예외 처리
- 모듈 책임 분리
- Service / Repository 구조
- 파일 기반 데이터의 안전한 수정
- `os.replace()`를 이용한 원자적 파일 교체
- 대용량 데이터 처리 시 메모리와 I/O 병목의 차이

---

## 최종 결과

이 프로젝트는 단순히 거래 데이터를 저장하는 프로그램이 아니라 다음 흐름을 고려하여 구현했습니다.

```text
사용자 CLI 입력
        ↓
입력 검증
        ↓
Service 업무 로직
        ↓
Repository 파일 처리
        ↓
JSONL 영구 저장
```

조회 시에는:

```text
JSONL 파일
   ↓
Generator
   ↓
Service 조건 처리
   ↓
CLI 출력
```

방식을 사용합니다.

이를 통해 기능 구현뿐 아니라 데이터 영속성, 예외 처리, 메모리 효율, 책임 분리, 데이터 안전성을 고려한 파일 기반 콘솔 애플리케이션을 구현했습니다.