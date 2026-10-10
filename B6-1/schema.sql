-- Codyssey B5-1: Cafe Order Management Schema (MySQL 8.4)
-- Reset database and create tables with proper constraints

DROP DATABASE IF EXISTS codyssey_cafe;
CREATE DATABASE codyssey_cafe DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE codyssey_cafe;

-- 1. customer (고객)
CREATE TABLE customer (
    customer_id INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    CONSTRAINT pk_customer PRIMARY KEY (customer_id),
    CONSTRAINT uq_customer_email UNIQUE (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. menu (메뉴)
CREATE TABLE menu (
    menu_id INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    category VARCHAR(30) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    CONSTRAINT pk_menu PRIMARY KEY (menu_id),
    CONSTRAINT uq_menu_name UNIQUE (name),
    CONSTRAINT chk_menu_price CHECK (price > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. orders (주문)
CREATE TABLE orders (
    order_id INT NOT NULL,
    customer_id INT NOT NULL,
    ordered_at DATETIME NOT NULL,
    status VARCHAR(20) NOT NULL,
    CONSTRAINT pk_orders PRIMARY KEY (order_id),
    CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id) REFERENCES customer (customer_id),
    CONSTRAINT chk_orders_status CHECK (status IN ('PAID', 'PENDING', 'CANCELLED'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. order_item (주문 상세 항목)
CREATE TABLE order_item (
    order_item_id INT NOT NULL,
    order_id INT NOT NULL,
    menu_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    CONSTRAINT pk_order_item PRIMARY KEY (order_item_id),
    CONSTRAINT fk_order_item_orders FOREIGN KEY (order_id) REFERENCES orders (order_id),
    CONSTRAINT fk_order_item_menu FOREIGN KEY (menu_id) REFERENCES menu (menu_id),
    CONSTRAINT chk_order_item_quantity CHECK (quantity > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
