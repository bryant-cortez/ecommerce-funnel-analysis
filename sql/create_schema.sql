
CREATE DATABASE ecommerce_analytics;

CREATE TABLE customers (
	customer_id VARCHAR(50) PRIMARY KEY, 
    signup_date DATE, 
    acquisition_source VARCHAR(50), 
    country VARCHAR(50)
);
CREATE TABLE products (
	product_id VARCHAR(20) PRIMARY KEY, 
    category VARCHAR(50),
    subcategory VARCHAR(50), 
    brand VARCHAR(50),
    price DECIMAL(12, 2)
);
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
CREATE TABLE order_items (
	order_id VARCHAR(20) PRIMARY KEY,
    product_id VARCHAR(20),
    unit_price DECIMAL(12, 2),
    quantity INT, 
    discount_pct DECIMAL (5, 2),
    line_total DECIMAL (12, 2), 
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
