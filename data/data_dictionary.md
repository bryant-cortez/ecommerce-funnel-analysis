# Data Dictionary: E-commerce Analytics Database

This document outlines the schema, tables, and fields for the E-commerce Analytics database.

## Table: `customers`
*Customer dimension: one record per customer. Stores customer signup information and acquisition attributes.*

| Column Name | Data Type | Description | Constraints |
| :--- | :--- | :--- | :--- |
| `customer_id` | VARCHAR(50) | Unique identifier for the customer | **Primary Key** |
| `signup_date` | DATE | Date the customer created an account | |
| `acquisition_source` | VARCHAR(50) | Marketing channel that acquired the customer | |
| `country` | VARCHAR(50) | Customer's country of residence | |

## Table: `products`
*Product dimension: one record per product. Stores product classification, brand, and listed price.*

| Column Name | Data Type | Description | Constraints |
| :--- | :--- | :--- | :--- |
| `product_id` | VARCHAR(20) | Unique identifier for the product | **Primary Key** |
| `category` | VARCHAR(50) | Top-level product category | |
| `subcategory` | VARCHAR(50) | Product subcategory | |
| `brand` | VARCHAR(50) | Product brand name | |
| `price` | DECIMAL(12,2) | Listed retail price | |

## Table: `orders`
*Orders table: one record per order. Links orders to customers and records transaction details.*

| Column Name | Data Type | Description | Constraints |
| :--- | :--- | :--- | :--- |
| `order_id` | VARCHAR(20) | Unique identifier for the order | **Primary Key** |
| `customer_id` | VARCHAR(50) | Identifier of the customer who placed the order | **Foreign Key** -> `customers` |
| `session_id` | VARCHAR(50) | Identifier of the web session where the order was placed | |
| `order_timestamp` | DATETIME | Date and time the order was placed | |
| `total_amount` | DECIMAL(12,2) | Total monetary value of the order | |
| `payment_method` | VARCHAR(50) | Method used for payment (e.g., Credit Card, PayPal) | |
| `order_status` | VARCHAR(30) | Current status of the order (e.g., Completed, Cancelled) | |

## Table: `events`
*Captures session activity, including event type, timestamp, product information, device, and traffic source.*

| Column Name | Data Type | Description | Constraints |
| :--- | :--- | :--- | :--- |
| `event_id` | VARCHAR(20) | Unique identifier for the event | **Primary Key** |
| `customer_id` | VARCHAR(50) | Identifier of the customer performing the event | **Foreign Key** -> `customers` |
| `session_id` | VARCHAR(20) | Identifier of the web session | |
| `event_timestamp` | DATETIME | Date and time the event occurred | |
| `event_type` | VARCHAR(30) | Type of action taken (e.g., view, add_to_cart, purchase) | |
| `product_id` | VARCHAR(20) | Identifier of the product involved in the event | **Foreign Key** -> `products` |
| `device` | VARCHAR(30) | Device used by the customer (e.g., mobile, desktop, tablet) | |
| `traffic_source` | VARCHAR(50) | Marketing channel that brought the user (e.g., social, organic) | |
| `category` | VARCHAR(50) | Top-level product category (denormalized for event tracking) | |
| `subcategory` | VARCHAR(50) | Product subcategory (denormalized for event tracking) | |
| `brand` | VARCHAR(50) | Product brand (denormalized for event tracking) | |
| `price` | DECIMAL(12,2) | Price of the product at the time of the event | |

## Table: `order_items`
*Stores product-level details associated with orders, including unit price, quantity, discount, and line total.*

| Column Name | Data Type | Description | Constraints |
| :--- | :--- | :--- | :--- |
| `order_id` | VARCHAR(20) | Identifier of the order | **Foreign Key** -> `orders` |
| `product_id` | VARCHAR(20) | Identifier of the product purchased | **Foreign Key** -> `products` |
| `unit_price` | DECIMAL(12,2) | Price per unit at the time of purchase | |
| `quantity` | INT | Number of units purchased | |
| `discount_pct` | DECIMAL(5,2) | Percentage discount applied to the line item | |
| `line_total` | DECIMAL(12,2) | Total cost for this line item (unit_price * quantity - discount) | |

> **Note:** A Composite Primary Key `(order_id, product_id)` is applied to the `order_items` table to allow multiple products to be included in a single order without violating primary key constraints.
