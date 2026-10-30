erDiagram
    CUSTOMERS ||--o{ ORDERS : "places"
    CUSTOMERS ||--o{ EVENTS : "triggers"
    ORDERS ||--|{ ORDER_ITEMS : "contains"
    PRODUCTS ||--o{ ORDER_ITEMS : "included in"
    PRODUCTS ||--o{ EVENTS : "viewed in"

    CUSTOMERS {
        VARCHAR(50) customer_id PK
        DATE signup_date
        VARCHAR(50) acquisition_source
        VARCHAR(50) country
    }

    PRODUCTS {
        VARCHAR(20) product_id PK
        VARCHAR(50) category
        VARCHAR(50) subcategory
        VARCHAR(50) brand
        DECIMAL(12,2) price
    }

    ORDERS {
        VARCHAR(20) order_id PK
        VARCHAR(50) customer_id FK
        VARCHAR(50) session_id
        DATETIME order_timestamp
        DECIMAL(12,2) total_amount
        VARCHAR(50) payment_method
        VARCHAR(30) order_status
    }

    EVENTS {
        VARCHAR(20) event_id PK
        VARCHAR(50) customer_id FK
        VARCHAR(20) session_id
        DATETIME event_timestamp
        VARCHAR(30) event_type
        VARCHAR(20) product_id FK
        VARCHAR(30) device
        VARCHAR(50) traffic_source
        VARCHAR(50) category
        VARCHAR(50) subcategory
        VARCHAR(50) brand
        DECIMAL(12,2) price
    }

    ORDER_ITEMS {
        VARCHAR(20) order_id PK, FK
        VARCHAR(20) product_id PK, FK
        DECIMAL(12,2) unit_price
        INT quantity
        DECIMAL(5,2) discount_pct
        DECIMAL(12,2) line_total
    }
