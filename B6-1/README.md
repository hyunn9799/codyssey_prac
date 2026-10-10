# Codyssey B5-1 | 카페 주문 관리 데이터베이스

## 1. 프로젝트 개요

- **분야:** AI/SW 기초 — 데이터베이스와 백엔드
- **주제:** 카페 주문 관리 시스템
- **목표:** 관계형 데이터베이스를 설계하고, SQL만으로 데이터 입력·조회·조인·집계·수정·삭제를 수행한다.
- **사용 기술:** MySQL 8.4, OrbStack(Docker), SQL, Bash
- **개발 방식:** 로컬 환경 / 백엔드 프레임워크 미사용

고객의 주문과 주문에 포함된 메뉴를 별도 테이블로 관리한다. 고객별 주문 횟수, 결제 완료 매출, 메뉴별 가격 등 서비스 운영에 필요한 정보를 SQL로 조회한다.

## 2. 프로젝트 구조

```text
codyssey_b5_1_cafe/
├── 01_schema.sql
├── 02_seed.sql
├── 03_queries.sql
├── scripts/
│   └── run_orbstack.sh
├── results/
│   ├── 00_validation.txt
│   └── Q01.txt ~ Q15.txt
├── STUDY_GUIDE.md
└── README.md
```

각 파일의 역할은 다음과 같다.

- `01_schema.sql`: 데이터베이스와 테이블 생성, PK/FK/제약조건 정의
- `02_seed.sql`: 각 테이블에 샘플 데이터 입력
- `03_queries.sql`: 필수 SQL 15개 작성
- `scripts/run_orbstack.sh`: MySQL 실행 및 SQL 실행 결과 저장
- `results/`: SQL별 실행 결과 및 검증 로그
- `STUDY_GUIDE.md`: 개념 설명 및 구두평가 학습 자료

`results` 폴더의 실제 실행 결과는 OrbStack에서 스크립트를 정상적으로 실행한 뒤 생성된다.

## 3. 데이터베이스 설계

### 3.1 테이블 구성

| 테이블 | 역할 | PK | 최초 데이터 |
|---|---|---|---:|
| customer | 고객 정보 관리 | customer_id | 12행 |
| menu | 메뉴 및 가격 관리 | menu_id | 10행 |
| orders | 주문 정보 관리 | order_id | 12행 |
| order_item | 주문별 상품 상세 관리 | order_item_id | 21행 |

4개 테이블 모두 PK를 가지며, 각 테이블에 최소 10행 이상의 데이터를 저장하도록 설계했다.

### 3.2 테이블 관계

```text
customer (1) ── (N) orders
                       |
                      (1)
                       |
                      (N)
                   order_item
                       |
                      (N)
                       |
                      (1)
                     menu
```

총 3개의 1:N 관계를 정의했다.

1. `customer → orders`: 고객 한 명이 여러 주문을 할 수 있다.
2. `orders → order_item`: 주문 한 건에 여러 메뉴가 포함될 수 있다.
3. `menu → order_item`: 메뉴 하나가 여러 주문에 포함될 수 있다.

예를 들어 `customer_id=1`인 김민수 고객은 주문 1번, 3번, 10번을 가지고 있다.

`customer.customer_id`는 PK이고, `orders.customer_id`는 FK이므로 고객과 주문을 연결할 수 있다.

### 3.3 테이블을 분리한 이유

고객 정보와 메뉴 정보를 주문 데이터마다 중복해서 저장하지 않기 위해 테이블을 분리했다.

- `customer`: 이름과 이메일을 한 곳에서 관리한다.
- `menu`: 메뉴 이름과 현재 판매 가격을 관리한다.
- `orders`: 주문 고객, 주문 시각, 주문 상태를 관리한다.
- `order_item`: 주문에 포함된 메뉴, 수량, 구매 당시 단가를 관리한다.

이렇게 설계하면 고객 정보나 메뉴 이름이 변경되더라도 불필요한 중복 수정이 발생하지 않는다.

또한 구매 당시 가격을 `order_item.unit_price`에 저장했기 때문에 메뉴 가격이 변경되어도 과거 주문 금액을 유지할 수 있다.

### 3.4 제약조건

| 제약조건 | 적용 목적 |
|---|---|
| PRIMARY KEY | 각 행을 유일하게 식별 |
| FOREIGN KEY | 존재하는 데이터만 참조하도록 제한 |
| NOT NULL | 필수 입력값 누락 방지 |
| UNIQUE | 이메일 및 메뉴 이름 중복 방지 |
| CHECK | 가격, 수량, 주문 상태의 유효성 검사 |

외래키 제약조건은 InnoDB 엔진을 통해 적용했다.

존재하지 않는 고객 ID로 주문을 생성하면 MySQL의 외래키 제약조건에 의해 입력이 거부된다.

### 3.5 자료형 선택 이유

| 자료형 | 사용 컬럼 | 이유 |
|---|---|---|
| INT | ID, 수량 | 정수 데이터 저장 |
| VARCHAR | 이름, 이메일 | 가변 길이 문자열 저장 |
| DECIMAL(10,2) | 가격, 단가 | 정확한 십진수 금액 저장 |
| DATETIME | 주문 시각 | 날짜와 시간을 함께 기록 |

금액은 부동소수점 오차를 피하기 위해 `FLOAT` 대신 `DECIMAL`을 사용했다.

## 4. 개발 환경 및 실행 방법

### 4.1 개발 환경

- OS: macOS
- 가상화 및 컨테이너: OrbStack
- 데이터베이스: MySQL 8.4
- SQL 실행: MySQL CLI
- 자동화: Bash Script

별도의 백엔드 프레임워크는 사용하지 않았다.

### 4.2 데이터베이스 실행

OrbStack을 실행한 뒤 프로젝트 최상위 폴더에서 다음 명령어를 실행한다.

```bash
chmod +x scripts/run_orbstack.sh
./scripts/run_orbstack.sh
```

스크립트는 다음 작업을 수행한다.

1. MySQL 8.4 컨테이너 생성 또는 시작
2. 데이터베이스와 4개 테이블 생성
3. 샘플 데이터 입력
4. SQL 15개 순차 실행
5. 쿼리별 결과 텍스트 저장
6. 테이블 수, 행 수, FK 제약조건 검증

**주의:** 실행 시 `codyssey_cafe` 데이터베이스를 초기화하므로 기존 데이터가 삭제된다. 실습 전용 데이터베이스에서만 실행해야 한다.

### 4.3 MySQL 접속 정보

| 항목 | 값 |
|---|---|
| Container | codyssey-mysql |
| Host | 127.0.0.1 |
| Port | 3307 |
| User | root |
| Database | codyssey_cafe |
| 초기 Password | codyssey_2026_demo |

비밀번호는 로컬 실습용 예시이며 실제 운영 환경에서 사용하지 않는다.

직접 접속하는 명령어는 다음과 같다.

```bash
docker exec -it codyssey-mysql mysql -uroot -p codyssey_cafe
```

접속 후 다음 SQL을 실행해 데이터베이스 상태를 확인할 수 있다.

```sql
SHOW TABLES;

SELECT * FROM customer;

SELECT * FROM menu;
```

## 5. 핵심 SQL 15개

과제에서 요구하는 SQL을 총 15개 작성했다.

| 번호 | 분류 | SQL 목적 |
|---|---|---|
| Q01 | 기본 조회 | 이름이 김으로 시작하는 고객 조회 |
| Q02 | 기본 조회 | 가격이 비싼 메뉴 TOP 3 |
| Q03 | 기본 조회 | 특정 기간의 주문 검색 |
| Q04 | 기본 조회 | 가격이 저렴한 메뉴 TOP 5 |
| Q05 | INNER JOIN | 주문과 고객 정보 연결 |
| Q06 | INNER JOIN | 주문 상세와 메뉴 연결 |
| Q07 | LEFT JOIN | 주문이 없는 고객까지 조회 |
| Q08 | 다중 JOIN | 고객·주문·상세·메뉴 연결 |
| Q09 | COUNT / GROUP BY | 고객별 주문 횟수 |
| Q10 | SUM / GROUP BY | 카테고리별 결제 매출 |
| Q11 | AVG / GROUP BY | 카테고리별 평균 가격 |
| Q12 | 서브쿼리 | 전체 평균보다 비싼 메뉴 |
| Q13 | UPDATE | 주문 상태 수정 |
| Q14 | DELETE | 테스트 고객 삭제 |
| Q15 | CREATE INDEX | 주문 날짜 인덱스 생성 |

유형별 개수는 다음과 같다.

- 기본 조회: 4개
- 조인: 4개 (INNER JOIN 2개 이상, LEFT JOIN 1개 이상)
- 집계: 3개 (COUNT, SUM, AVG)
- 서브쿼리: 1개
- 수정/삭제: 2개
- 인덱스: 1개

**총 15개이며, 각 쿼리에는 목적을 설명하는 주석을 작성했다.**

## 6. 인덱스 설계

주문 날짜를 기준으로 데이터를 검색하거나 정렬하는 작업을 고려하여 `orders.ordered_at`에 인덱스를 생성했다.

```sql
CREATE INDEX idx_orders_ordered_at
ON orders (ordered_at);
```

인덱스를 사용하면 많은 데이터에서 특정 날짜 범위를 조회하는 작업을 효율적으로 수행할 수 있다.

다만 인덱스는 별도의 저장 공간을 사용하고 데이터 변경 시 유지 비용이 발생하므로, 검색과 정렬에 활용하는 컬럼을 기준으로 선택했다.

샘플 데이터가 적기 때문에 이 실습에서 실제 조회 속도 향상이 반드시 나타나는 것은 아니다.

## 7. SQL 실행 결과 검증

### 7.1 실행 결과 저장

`run_orbstack.sh`는 쿼리마다 실행 결과를 다음과 같이 저장하도록 구성했다.

```text
results/
├── 00_validation.txt
├── Q01.txt
├── Q02.txt
├── ...
├── Q14.txt
└── Q15.txt
```

Q01~Q12는 SELECT 결과를 저장한다.

Q13~Q15는 데이터를 수정하거나 인덱스를 생성하는 SQL이므로 추가 확인 쿼리의 결과를 함께 저장한다.

### 7.2 데이터 건수 확인

샘플 데이터 입력과 수정·삭제 쿼리를 순서대로 실행한 후 예상되는 행 수는 다음과 같다.

| 테이블 | 최종 예상 행 수 |
|---|---:|
| customer | 11 |
| menu | 10 |
| orders | 12 |
| order_item | 21 |

삭제 실습 이후에도 모든 테이블에 최소 10행 이상의 데이터를 유지한다.

확인 SQL은 다음과 같다.

```sql
SELECT COUNT(*) FROM customer;
SELECT COUNT(*) FROM menu;
SELECT COUNT(*) FROM orders;
SELECT COUNT(*) FROM order_item;
```

### 7.3 FK 무결성 확인

존재하지 않는 고객을 참조하는 주문을 추가하여 FK 제약조건이 동작하는지 테스트한다.

```sql
INSERT INTO orders
(order_id, customer_id, ordered_at, status)
VALUES
(9999, 99999, NOW(), 'PAID');
```

`customer_id=99999`가 존재하지 않으므로 정상적인 MySQL 환경에서는 외래키 오류 `ERROR 1452`가 발생해야 한다.

이 결과를 통해 존재하지 않는 고객의 주문을 저장하지 못하도록 제한했는지 확인한다.

**실제 PASS 여부는 OrbStack에서 실행한 `00_validation.txt`와 Q01~Q15 결과 파일을 확인하여 판단한다.**

## 8. 주요 학습 내용 및 문제 해결 접근

### 8.1 PK, FK, 1:N 관계 이해

PK는 테이블의 각 행을 구분하는 고유 식별자이고, FK는 서로 다른 테이블의 데이터를 연결하는 역할을 한다.

고객 한 명에 여러 주문이 연결되므로 1:N 관계가 성립한다.

### 8.2 INNER JOIN과 LEFT JOIN 차이

`INNER JOIN`은 두 테이블에서 일치하는 행만 반환한다.

`LEFT JOIN`은 왼쪽 테이블의 모든 행을 유지하고, 오른쪽에 일치하는 데이터가 없으면 NULL을 반환한다.

Q07에서는 주문이 없는 고객도 조회하기 위해 LEFT JOIN을 사용했다.

### 8.3 GROUP BY와 집계 함수

`GROUP BY`는 특정 컬럼의 값이 같은 데이터를 그룹으로 묶는다.

- `COUNT`: 데이터 개수 계산
- `SUM`: 값의 합계 계산
- `AVG`: 평균값 계산

Q09에서는 주문하지 않은 고객의 주문 횟수를 0으로 표시하기 위해 `COUNT(*)` 대신 `COUNT(o.order_id)`를 사용했다.

`COUNT(컬럼)`은 NULL을 제외하고 계산하기 때문이다.

### 8.4 가장 복잡한 SQL: Q08

가장 복잡한 쿼리는 고객, 주문, 주문 상세, 메뉴 등 4개 테이블을 연결하는 JOIN 쿼리이다.

해결 과정은 다음과 같다.

1. `orders`를 기준으로 고객 테이블 연결
2. 주문 ID를 이용해 주문 상세 연결
3. 메뉴 ID를 이용해 메뉴 이름 조회
4. 수량과 구매 당시 단가를 곱해 금액 계산

이를 통해 여러 테이블로 분리된 데이터를 관계에 따라 하나의 조회 결과로 결합할 수 있음을 확인한다.

### 8.5 주요 문제 해결 방법

**문제 1. FK 참조 무결성**

부모 데이터가 존재하지 않으면 자식 데이터를 입력할 수 없으므로, 고객·메뉴·주문 데이터를 먼저 생성한 후 주문 상세 데이터를 입력하도록 INSERT 순서를 구성했다.

**문제 2. 주문이 없는 고객의 집계**

LEFT JOIN에서는 주문이 없는 고객도 NULL이 포함된 결과 행 하나를 가지므로 `COUNT(*)`를 사용하면 1건으로 계산될 수 있다.

이를 해결하기 위해 `COUNT(o.order_id)`를 사용하여 실제 주문이 존재하는 경우만 집계하도록 했다.

**문제 3. 수정과 삭제 결과 확인**

UPDATE와 DELETE는 SELECT처럼 조회 결과를 반환하지 않으므로, 변경 후 별도의 SELECT 문으로 데이터를 확인하도록 구성했다.

## 9. 평가 항목 확인

- [ ] 최소 4개 테이블 및 각 테이블 PK 정의
- [ ] FK를 이용한 1:N 관계 최소 2개
- [ ] 존재하지 않는 FK 참조 차단 확인
- [ ] 테이블별 샘플 데이터 최소 10행
- [ ] 필수 SQL 15개 작성
- [ ] SQL 15개의 실행 결과 텍스트 저장
- [ ] 테이블 분리 이유와 각 테이블의 역할 설명 가능
- [ ] PK/FK와 1:N 관계 설명 가능
- [ ] 자료형 및 인덱스 선택 이유 설명 가능
- [ ] INNER JOIN과 LEFT JOIN 차이 설명 가능
- [ ] GROUP BY 및 COUNT/SUM/AVG 설명 가능
- [ ] 복잡한 쿼리의 해결 과정 설명 가능

## 10. 최종 제출물

필수 제출 자료는 다음과 같다.

1. `01_schema.sql` — 스키마 생성 SQL
2. `02_seed.sql` — 샘플 데이터 입력 SQL
3. `03_queries.sql` — 핵심 SQL 15개
4. `results/` — 실제 SQL 실행 결과 텍스트

추가 자료로 `README.md`, `STUDY_GUIDE.md`, `scripts/run_orbstack.sh`를 함께 첨부한다.

ERD 이미지와 보너스 과제는 필수 제출 범위에서 제외했다.