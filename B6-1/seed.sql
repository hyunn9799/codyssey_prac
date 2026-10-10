-- Codyssey B5-1: Deterministic meaningful test data (MySQL 8.4)
-- Run after 01_schema.sql. Parent tables first, then child tables.
USE codyssey_cafe;

INSERT INTO customer (customer_id, name, email) VALUES
(1, '김민수', 'minsu@example.com'),
(2, '이지은', 'jieun@example.com'),
(3, '박준호', 'junho@example.com'),
(4, '최수진', 'sujin@example.com'),
(5, '정하늘', 'haneul@example.com'),
(6, '오지훈', 'jihoon@example.com'),
(7, '한유진', 'yujin@example.com'),
(8, '강도윤', 'doyoon@example.com'),
(9, '윤서아', 'seoa@example.com'),
(10, '임지호', 'jiho@example.com'),
(11, '조하린', 'harin@example.com'),
(12, '데모삭제대상', 'delete@example.com');

INSERT INTO menu (menu_id, name, category, price) VALUES
(1, '아메리카노', 'COFFEE', 4500.00),
(2, '카페라테', 'COFFEE', 5000.00),
(3, '바닐라라테', 'COFFEE', 5500.00),
(4, '콜드브루', 'COFFEE', 5200.00),
(5, '카푸치노', 'COFFEE', 5000.00),
(6, '녹차라테', 'TEA', 5500.00),
(7, '캐모마일티', 'TEA', 4800.00),
(8, '레몬에이드', 'BEVERAGE', 5800.00),
(9, '치즈케이크', 'DESSERT', 6500.00),
(10, '초코쿠키', 'DESSERT', 2500.00);

INSERT INTO orders (order_id, customer_id, ordered_at, status) VALUES
(1, 1, '2026-10-01 09:20:00', 'PAID'),
(2, 2, '2026-10-01 12:15:00', 'PAID'),
(3, 1, '2026-10-02 08:40:00', 'PAID'),
(4, 3, '2026-10-02 13:10:00', 'PAID'),
(5, 4, '2026-10-03 10:05:00', 'CANCELLED'),
(6, 5, '2026-10-04 15:45:00', 'PAID'),
(7, 2, '2026-10-05 11:30:00', 'PAID'),
(8, 6, '2026-10-05 16:05:00', 'PAID'),
(9, 7, '2026-10-06 14:00:00', 'PAID'),
(10, 1, '2026-10-07 09:00:00', 'PAID'),
(11, 8, '2026-10-08 17:25:00', 'PAID'),
(12, 9, '2026-10-09 10:35:00', 'PENDING');

-- unit_price stores the price at purchase time, even if menu.price changes later.
INSERT INTO order_item (order_item_id, order_id, menu_id, quantity, unit_price) VALUES
(1, 1, 1, 2, 4500.00),
(2, 1, 10, 1, 2500.00),
(3, 2, 2, 1, 5000.00),
(4, 2, 9, 1, 6500.00),
(5, 3, 3, 1, 5500.00),
(6, 3, 8, 1, 5800.00),
(7, 4, 4, 2, 5200.00),
(8, 5, 5, 1, 5000.00),
(9, 6, 6, 1, 5500.00),
(10, 6, 10, 2, 2500.00),
(11, 7, 1, 1, 4500.00),
(12, 7, 9, 2, 6500.00),
(13, 8, 7, 2, 4800.00),
(14, 9, 8, 1, 5800.00),
(15, 9, 10, 1, 2500.00),
(16, 10, 2, 2, 5000.00),
(17, 10, 9, 1, 6500.00),
(18, 11, 4, 1, 5200.00),
(19, 11, 6, 1, 5500.00),
(20, 12, 3, 2, 5500.00),
(21, 12, 10, 1, 2500.00);