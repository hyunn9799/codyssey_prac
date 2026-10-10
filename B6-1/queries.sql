-- Codyssey B5-1: 15 Essential SQL Queries (MySQL 8.4)
USE codyssey_cafe;

-- ==============================================================================
-- 1. 기본 조회 (Q01 ~ Q04)
-- ==============================================================================

-- Q01_START
-- Q01: 전체 메뉴 목록을 가격이 높은 순서로 정렬하여 조회
SELECT menu_id, name, category, price
FROM menu
ORDER BY price DESC;
-- Q01_END

-- Q02_START
-- Q02: 등록된 모든 고객의 번호, 이름, 이메일 조회
SELECT customer_id, name, email
FROM customer
ORDER BY customer_id ASC;
-- Q02_END

-- Q03_START
-- Q03: 결제 완료(PAID) 상태의 주문 내역을 최근 주문일시 순으로 조회
SELECT order_id, customer_id, ordered_at, status
FROM orders
WHERE status = 'PAID'
ORDER BY ordered_at DESC;
-- Q03_END

-- Q04_START
-- Q04: 가격이 5,000원 이상인 커피(COFFEE) 메뉴 목록 조회
SELECT menu_id, name, category, price
FROM menu
WHERE category = 'COFFEE' AND price >= 5000.00
ORDER BY price DESC;
-- Q04_END


-- ==============================================================================
-- 2. JOIN 쿼리 (Q05 ~ Q08: INNER JOIN >= 2, LEFT JOIN >= 1)
-- ==============================================================================

-- Q05_START
-- Q05: 주문 목록과 해당 주문을 진행한 고객의 이름 조회 (INNER JOIN)
SELECT o.order_id, c.customer_id, c.name AS customer_name, o.ordered_at, o.status
FROM orders o
INNER JOIN customer c ON o.customer_id = c.customer_id
ORDER BY o.order_id ASC;
-- Q05_END

-- Q06_START
-- Q06: 주문 상세 품목별 메뉴명, 주문 수량, 단가 및 소계 금액 조회 (INNER JOIN)
SELECT oi.order_item_id, oi.order_id, m.name AS menu_name, oi.quantity, oi.unit_price, (oi.quantity * oi.unit_price) AS subtotal
FROM order_item oi
INNER JOIN menu m ON oi.menu_id = m.menu_id
ORDER BY oi.order_id ASC, oi.order_item_id ASC;
-- Q06_END

-- Q07_START
-- Q07: 고객명, 주문 번호, 주문한 메뉴명, 수량 및 주문 단가 조회 (3개 테이블 INNER JOIN)
SELECT o.order_id, c.name AS customer_name, m.name AS menu_name, oi.quantity, oi.unit_price
FROM orders o
INNER JOIN customer c ON o.customer_id = c.customer_id
INNER JOIN order_item oi ON o.order_id = oi.order_id
INNER JOIN menu m ON oi.menu_id = m.menu_id
ORDER BY o.order_id ASC, m.name ASC;
-- Q07_END

-- Q08_START
-- Q08: 모든 고객과 고객의 주문 현황 조회 - 주문이 없는 고객도 포함 (LEFT JOIN)
SELECT c.customer_id, c.name AS customer_name, o.order_id, o.ordered_at, o.status
FROM customer c
LEFT JOIN orders o ON c.customer_id = o.customer_id
ORDER BY c.customer_id ASC, o.order_id ASC;
-- Q08_END


-- ==============================================================================
-- 3. GROUP BY 및 집계 함수 (Q09 ~ Q11: COUNT, SUM, AVG)
-- ==============================================================================

-- Q09_START
-- Q09: 메뉴 카테고리별 등록 메뉴 수와 평균 가격 집계 (COUNT, AVG)
SELECT category, COUNT(*) AS menu_count, ROUND(AVG(price), 2) AS avg_price
FROM menu
GROUP BY category
ORDER BY avg_price DESC;
-- Q09_END

-- Q10_START
-- Q10: 고객별 총 주문 횟수 집계 (주문 이력이 없는 고객 포함, COUNT)
SELECT c.customer_id, c.name AS customer_name, COUNT(o.order_id) AS total_orders
FROM customer c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_orders DESC, c.customer_id ASC;
-- Q10_END

-- Q11_START
-- Q11: 주문별 총 결제 금액 합계 계산 (SUM)
SELECT o.order_id, o.status, SUM(oi.quantity * oi.unit_price) AS total_amount
FROM orders o
INNER JOIN order_item oi ON o.order_id = oi.order_id
GROUP BY o.order_id, o.status
ORDER BY total_amount DESC;
-- Q11_END

-- ==============================================================================
-- 4. 서브쿼리 (Q12)
-- ==============================================================================

-- Q12_START
-- Q12: 전체 메뉴의 평균 가격보다 비싼 메뉴 목록 조회 (서브쿼리)
SELECT menu_id, name, category, price
FROM menu
WHERE price > (SELECT AVG(price) FROM menu)
ORDER BY price DESC;
-- Q12_END


-- ==============================================================================
-- 5. 데이터 수정 / 삭제 (Q13, Q14)
-- ==============================================================================

-- Q13_START
-- Q13: 대기 상태(PENDING)인 12번 주문을 결제 완료(PAID) 상태로 수정
UPDATE orders
SET status = 'PAID'
WHERE order_id = 12;
-- Q13_END

-- Q14_START
-- Q14: 주문 이력이 없는 12번 탈퇴/테스트 고객 데이터 삭제
DELETE FROM customer
WHERE customer_id = 12;
-- Q14_END


-- ==============================================================================
-- 6. 인덱스 생성 (Q15)
-- ==============================================================================

-- Q15_START
-- Q15: 주문 일시(ordered_at) 컬럼에 인덱스 생성 (기간 검색 및 정렬 성능 향상)
CREATE INDEX idx_orders_ordered_at ON orders (ordered_at);
-- Q15_END
