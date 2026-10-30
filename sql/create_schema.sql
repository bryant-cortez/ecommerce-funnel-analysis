-- =========================================================
-- E-commerce Analytics Database
-- Purpose: Create the relational schema for customer,
-- product, order, order-item, and event-level data.
-- =========================================================
CREATE DATABASE ecommerce_analytics;


-- Customer dimension: one record per customer.
-- Stores customer signup information and acquisition attributes.
CREATE TABLE customers (
	customer_id VARCHAR(50) PRIMARY KEY, 
    signup_date DATE, 
    acquisition_source VARCHAR(50), 
    country VARCHAR(50)
);


-- Product dimension: one record per product.
-- Stores product classification, brand, and listed price.
CREATE TABLE products (
	product_id VARCHAR(20) PRIMARY KEY, 
    category VARCHAR(50),
    subcategory VARCHAR(50), 
    brand VARCHAR(50),
    price DECIMAL(12, 2)
);


-- Orders table: one record per order.
-- Links orders to customers and records transaction details.
CREATE TABLE orders (
	order_id VARCHAR(20) PRIMARY KEY, 
    customer_id VARCHAR(50),
    session_id VARCHAR(50), 
    order_timestamp DATETIME, 
    total_amount DECIMAL(12, 2),
    payment_method VARCHAR(50), 
    order_status VARCHAR(30),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);


-- Events table: one record per tracked event.
-- Captures session activity, including event type, timestamp,
-- product information, device, and traffic source.
CREATE TABLE events (
	event_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(50),
    session_id VARCHAR(20),
    event_timestamp DATETIME, 
    event_type VARCHAR(30), 
    product_id VARCHAR(20), 
    device VARCHAR(30),
    traffic_source VARCHAR(50),
    category VARCHAR(50),
    subcategory VARCHAR(50),
    brand VARCHAR(50),
    price DECIMAL(12, 2),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);


-- Order items table: stores product-level details associated
-- with orders, including unit price, quantity, discount, and
-- line total.
CREATE TABLE order_items (
	order_id VARCHAR(20),
    product_id VARCHAR(20),
    unit_price DECIMAL(12, 2),
    quantity INT, 
    discount_pct DECIMAL (5, 2),
    line_total DECIMAL (12, 2), 
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
