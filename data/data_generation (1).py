#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
from faker import Faker 
import datetime as dt
import matplotlib.pyplot as plt
from pathlib import Path


# In[2]:


def create_customer_data(n_rows: int, seed: int):
    fake = Faker(locale="en_US")
    fake.seed_instance(seed)
    np.random.seed(seed)

    customer_ids = []
    signup_dates = []
    acquisition_sources = []
    countries = []

    start_date = dt.date(2025, 1, 1)
    end_date = dt.date(2026, 6, 1)

    possible_sources = ["Organic Search", "Paid Search", "Social", 
                        "Email", "Direct", "Referral"]

    possible_countries = ["US", "Canada", "UK", "Australia", 
                          "Germany", "France"]

    for _ in range(n_rows):
        customer_ids.append(fake.uuid4())

        signup_dates.append(fake.date_between(start_date=start_date, 
                                             end_date=end_date))

        acquisition_sources.append(np.random.choice(a=possible_sources, 
                                                   p=[0.13, 0.28, 0.23, 
                                                      0.18, 0.06, 
                                                      0.12]))

        countries.append(np.random.choice(a=possible_countries, 
                                        p=[0.44, 0.17, 0.12, 
                                           0.07, 0.11, 0.09]))

    cust_table = pd.DataFrame({
        "customer_id": customer_ids, 
        "signup_date": signup_dates, 
        "acquisition_source": acquisition_sources, 
        "country": countries})

    return cust_table
        
    
    


# In[3]:


customer_base_table = create_customer_data(50000, 42)


# In[4]:


customer_base_table.head()


# In[ ]:





# In[ ]:





# In[5]:


def create_product_data(n_rows: int, seed: int):
    np.random.seed(seed)

    product_ids = [f"P{i:04d}" for i in range(1, n_rows+1)]
    categories = []
    brands = []
    prices = []

    possible_categories = ["Apparel", "Footwear", "Accessories", 
                           "Sportswear", 
                           "Home and Lifestyle"]

    possible_brands = [
    "Nike", "Adidas", "Puma", "Under Armour", "New Balance",
    "Reebok", "Champion", "Levi's", "Wrangler",
    "The North Face", "Columbia", "Patagonia", "Converse",
    "Vans", "Timberland", "Dr. Martens", "ASICS", "Skechers",
    "Brooks", "Hoka", "Carhartt", "Dickies", "Hanes", "Gap",
    "Lacoste", "Calvin Klein", "Tommy Hilfiger", "Fossil",
    "Herschel","Osprey"]

    subcategories = []

    subcategory_map = {
        "Apparel": ["T-Shirts", "Hoodies", "Jackets", "Pants"], 
        "Footwear": ["Sneakers", "Boots", "Sandals"], 
        "Accessories": ["Bags", "Hats", "Belts"],
        "Sportswear": ["Activewear", "Running", "Training"],
        "Home and Lifestyle": ["Water Bottles", 
                               "Decor", 
                               "Cosmetics"]}

    brand_map = {
    "Apparel": [
        "Nike", "Adidas", "Puma", "Under Armour", "Champion",
        "Levi's", "Wrangler", "The North Face", "Columbia",
        "Patagonia", "Carhartt", "Dickies", "Hanes", "Gap",
        "Lacoste", "Calvin Klein", "Tommy Hilfiger"
    ],

    "Footwear": [
        "Nike", "Adidas", "Puma", "New Balance", "Reebok",
        "Converse", "Vans", "Timberland", "Dr. Martens",
        "ASICS", "Skechers", "Brooks", "Hoka"
    ],

    "Accessories": [
        "Nike", "Adidas", "Puma", "Under Armour", "Champion",
        "Levi's", "Calvin Klein", "Tommy Hilfiger", "Fossil",
        "Herschel", "Osprey", "Carhartt", "Dickies"
    ],

    "Sportswear": [
        "Nike", "Adidas", "Puma", "Under Armour", "New Balance",
        "Reebok", "Champion", "ASICS", "Brooks", "Hoka",
        "The North Face", "Columbia", "Patagonia"
    ],

    "Home and Lifestyle": [
        "Bath and Body Works", "Herschel", "Osprey", "The North Face",
        "Columbia", "Patagonia", "Nike", "Adidas"
    ]
}
    price_ranges = {
        "T-Shirts": (11, 38), 
        "Hoodies": (18, 60), 
        "Jackets": (35, 85), 
        "Pants": (25, 65), 
        "Sneakers": (32, 212), 
        "Boots": (40, 115), 
        "Sandals": (8, 28), 
        "Bags": (15, 45), 
        "Hats": (15, 30), 
        "Belts": (8, 20), 
        "Activewear": (25, 90), 
        "Running": (22, 65), 
        "Training": (20, 55), 
        "Water Bottles": (11, 25), 
        "Decor": (18, 45), 
        "Cosmetics": (8, 32)}
    
    
    subcategory_probabilities = {
        "Apparel": [0.28, 0.19, 0.23, 0.30], 
        "Footwear": [0.61, 0.17, 0.22], 
        "Accessories": [0.44, 0.32, 0.24], 
        "Sportswear": [0.41, 0.25, 0.34], 
        "Home and Lifestyle": [0.11, 0.55, 0.34]}

    brand_probabilities = {
    "Apparel": [
        0.10, 0.09, 0.06, 0.04, 0.08, 0.09, 0.07, 0.06, 0.05,
        0.04, 0.06, 0.05, 0.03, 0.06, 0.04, 0.03, 0.05
    ],

    "Footwear": [
        0.16, 0.13, 0.08, 0.10, 0.07, 0.07, 0.08, 0.07, 0.05,
        0.07, 0.05, 0.04, 0.03
    ],

    "Accessories": [
        0.10, 0.08, 0.06, 0.07, 0.08, 0.10, 0.07, 0.07, 0.12,
        0.10, 0.07, 0.05, 0.03
    ],

    "Sportswear": [
        0.16, 0.14, 0.09, 0.13, 0.07, 0.06, 0.06, 0.08, 0.07,
        0.05, 0.03, 0.03, 0.03
    ],

    "Home and Lifestyle": [
        0.15, 0.20, 0.15, 0.12, 0.10, 0.10, 0.10, 0.08
    ]
}

                            

    for _ in range(n_rows):
        categories.append(np.random.choice(a=possible_categories, 
                                           p=[0.3, 0.15, 0.16, 
                                              0.20, 0.19]))
        

    for category in categories:
        possible_subcategories = subcategory_map[category]
        probabilities = subcategory_probabilities[category]
        subcategories.append(np.random.choice(a=possible_subcategories, 
                                              p=probabilities))

        possible_brands = brand_map[category]
        brand_probs = brand_probabilities[category]
        brands.append(np.random.choice(a=possible_brands, 
                                       p=brand_probs))

    for subcategory in subcategories:
        min_price = min(price_ranges[subcategory])
        max_price = max(price_ranges[subcategory])
        median_price = np.sqrt(min_price * max_price)
        mean_price = np.log(median_price)
        price = np.random.lognormal(mean=mean_price, sigma=0.4)

        while price < min_price or price > max_price:
            price = np.random.lognormal(mean=mean_price, sigma=0.4)

        prices.append(round(price, 2))
    

    product_table = pd.DataFrame({
    "product_id": product_ids, 
    "category": categories, 
    "subcategory": subcategories, 
    "brand": brands, 
    "price": prices})

    return product_table


# In[6]:


product_base_table = create_product_data(500, 42)


# In[7]:


product_base_table.head()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[8]:


def create_event_data(customers, products, seed):
    np.random.seed(seed)

    sessions_per_customer = np.random.geometric(
        p=0.20, size=len(customers)
    )

    customer_ids = np.repeat(
        customers["customer_id"],
        repeats=sessions_per_customer
    )

    session_ids = [
        f"S{i:06d}" for i in range(1, len(customer_ids) + 1)
    ]

    possible_devices = ["mobile", "desktop", "tablet"]
    possible_traffic_sources = [
        "Organic Search", "Paid Search", "Social",
        "Email", "Direct", "Referral"
    ]

    sessions = pd.DataFrame({
        "customer_id": customer_ids,
        "session_id": session_ids
    })

    sessions = sessions.merge(
        customers[["customer_id", "signup_date"]],
        how="left",
        on="customer_id"
    )
    sessions["signup_date"] = pd.to_datetime(sessions["signup_date"])

    end_timestamp = dt.datetime(2026, 6, 2)
    max_seconds = (
        end_timestamp - sessions["signup_date"]
    ).dt.total_seconds()

    random_seconds = (
        np.random.uniform(size=len(sessions)) * max_seconds
    )

    sessions["session_timestamp"] = (
        sessions["signup_date"]
        + pd.to_timedelta(random_seconds, unit="s")
    )

    num_sessions = len(sessions)

    sessions["device"] = np.random.choice(
        possible_devices,
        p=[0.54, 0.32, 0.14],
        size=num_sessions
    )

    sessions["traffic_source"] = np.random.choice(
        possible_traffic_sources,
        p=[0.11, 0.32, 0.21, 0.10, 0.08, 0.18],
        size=num_sessions
    )

    num_views_per_session = []

    for _ in range(num_sessions):
        if np.random.random() < 0.05:
            num_views = 0
        else:
            return_label = np.random.choice(
                ["1", "2-3", "4-6", "7-12"],
                p=[0.25, 0.35, 0.25, 0.15]
            )

            if return_label == "1":
                num_views = 1
            elif return_label == "2-3":
                num_views = np.random.randint(2, 4)
            elif return_label == "4-6":
                num_views = np.random.randint(4, 7)
            else:
                num_views = np.random.randint(7, 13)

        num_views_per_session.append(num_views)

    view_row_positions = np.repeat(
        np.arange(num_sessions),
        repeats=num_views_per_session
    )

    view_events = sessions.iloc[view_row_positions].copy()

    sessions["session_duration"] = np.random.uniform(
        low=60, high=1800, size=num_sessions
    )

    view_events = view_events.merge(
        sessions[["session_id", "session_duration"]],
        how="left",
        on="session_id"
    )

    view_offset = np.random.uniform(
        low=0,
        high=view_events["session_duration"].to_numpy(),
        size=len(view_events)
    )

    view_events["event_timestamp"] = (
        view_events["session_timestamp"]
        + pd.to_timedelta(view_offset, unit="s")
    )

    view_events["event_type"] = "view"

    view_events["product_id"] = np.random.choice(
        products["product_id"],
        size=len(view_events),
        replace=True
    )

    view_events = view_events.merge(
        products[
            ["product_id", "category", "subcategory", "brand", "price"]
        ],
        how="left",
        on="product_id"
    )

    cart_probability = np.where(view_events["traffic_source"].eq("Social"),
                                0.05, 0.11)

    view_events["proceeded"] = np.random.random(size=len(view_events)) <= cart_probability

    cart_events = view_events.loc[
        view_events["proceeded"]
    ].copy()

    cart_events["view_timestamp"] = cart_events["event_timestamp"]
    cart_events["event_type"] = "add_to_cart"

    cart_offset = np.random.uniform(
        low=5, high=180, size=len(cart_events)
    )

    session_end = (
        cart_events["session_timestamp"]
        + pd.to_timedelta(
            cart_events["session_duration"], unit="s"
        )
    )

    time_remaining = (
        session_end - cart_events["view_timestamp"]
    ).dt.total_seconds()

    valid_cart_mask = time_remaining > 1

    cart_events = cart_events.loc[valid_cart_mask].copy()
    cart_offset = cart_offset[valid_cart_mask]
    time_remaining = time_remaining[valid_cart_mask]

    cart_offset = np.minimum(cart_offset, time_remaining - 1)

    cart_events["event_timestamp"] = (
        cart_events["view_timestamp"]
        + pd.to_timedelta(cart_offset, unit="s")
    )

    assert (
        cart_events["event_timestamp"] > cart_events["view_timestamp"]
    ).all()

    assert (
        cart_events["event_timestamp"]
        <= (
            cart_events["session_timestamp"]
            + pd.to_timedelta(
                cart_events["session_duration"], unit="s"
            )
        )
    ).all()

    view_events = view_events.drop(columns="proceeded")

    
    cart_events["proceeded_to_checkout"] = (
        np.random.random(size=len(cart_events)) < 0.60
    )

    checkout_events = cart_events.loc[
        cart_events["proceeded_to_checkout"]
    ].copy()

    checkout_events["cart_timestamp"] = (
        checkout_events["event_timestamp"]
    )

    checkout_events["event_type"] = "checkout"

    session_end = (
        checkout_events["session_timestamp"]
        + pd.to_timedelta(
            checkout_events["session_duration"], unit="s"
        )
    )

    time_remaining = (
        session_end - checkout_events["cart_timestamp"]
    ).dt.total_seconds()

    valid_checkout_mask = time_remaining > 1

    checkout_events = checkout_events.loc[
        valid_checkout_mask
    ].copy()

    time_remaining = time_remaining.loc[valid_checkout_mask]

    
    checkout_offset = np.random.uniform(
        low=5,
        high=180,
        size=len(checkout_events)
    )

    checkout_offset = np.minimum(
        checkout_offset,
        time_remaining.to_numpy() - 1
    )

    checkout_events["event_timestamp"] = (
        checkout_events["cart_timestamp"]
        + pd.to_timedelta(checkout_offset, unit="s")
    )

    assert (
        checkout_events["event_timestamp"]
        > checkout_events["cart_timestamp"]
    ).all()

    assert (
        checkout_events["event_timestamp"]
        <= (
            checkout_events["session_timestamp"]
            + pd.to_timedelta(
                checkout_events["session_duration"], unit="s"
            )
        )
    ).all()

    
    purchase_probability = np.where(checkout_events["device"].eq("tablet"), 
                                    0.45, 0.75)
    checkout_events["proceeded_to_purchase"] = np.random.random(size=len(checkout_events)) < purchase_probability

    purchase_events = checkout_events.loc[
        checkout_events["proceeded_to_purchase"]
    ].copy()

    purchase_events["checkout_timestamp"] = (
        purchase_events["event_timestamp"]
    )

    purchase_events["event_type"] = "purchase"

    session_end = (
        purchase_events["session_timestamp"]
        + pd.to_timedelta(
            purchase_events["session_duration"], unit="s"
        )
    )

    time_remaining = (
        session_end - purchase_events["checkout_timestamp"]
    ).dt.total_seconds()

    valid_purchase_mask = time_remaining > 1

    purchase_events = purchase_events.loc[
        valid_purchase_mask
    ].copy()

    time_remaining = time_remaining.loc[valid_purchase_mask]


    purchase_offset = np.random.uniform(
        low=5,
        high=120,
        size=len(purchase_events)
    )

    purchase_offset = np.minimum(
        purchase_offset,
        time_remaining.to_numpy() - 1
    )

    purchase_events["event_timestamp"] = (
        purchase_events["checkout_timestamp"]
        + pd.to_timedelta(purchase_offset, unit="s")
    )

    assert (
        purchase_events["event_timestamp"]
        > purchase_events["checkout_timestamp"]
    ).all()

    assert (
        purchase_events["event_timestamp"]
        <= (
            purchase_events["session_timestamp"]
            + pd.to_timedelta(
                purchase_events["session_duration"], unit="s"
            )
        )
    ).all()

    event_columns = ["customer_id", "session_id", "event_timestamp",
                    "event_type", "product_id", "device", 
                    "traffic_source", "category", "subcategory", 
                    "brand", "price"]

    view_events_final = view_events[event_columns].copy()

    cart_events_final = cart_events[event_columns].copy()
    
    checkout_events_final = checkout_events[event_columns].copy()
    
    purchase_events_final = purchase_events[event_columns].copy()

    events = pd.concat([view_events_final, cart_events_final, 
                        checkout_events_final, purchase_events_final], 
                       ignore_index=True)

    events = events.sort_values(by=["session_id", "event_timestamp"]).reset_index(drop=True)

    events.insert(loc=0, column="event_id", 
                  value=[f"E{i:04d}" for i in range(1, len(events) + 1)]
                 )
    return events
    


# In[9]:


events_base_table = create_event_data(customer_base_table, product_base_table, seed=42)


# In[10]:


def create_order_data(events, products, seed: int):
    np.random.seed(seed)

    purchase_events = events.loc[events["event_type"] == "purchase"].copy()

    purchase_events = purchase_events.reset_index(drop=True)

    purchase_events["order_id"] = [f"O{i:07d}" for i in range(1, len(purchase_events) + 1)]

    possible_payment_methods = ["Credit Card", "PayPal", "Apple Pay", "Klarna"]
    payment_probabilities = [0.48, 0.22, 0.20, 0.10]

    purchase_events["payment_method"] = np.random.choice(a=possible_payment_methods, 
    p=payment_probabilities, size=len(purchase_events))

    purchase_events["order_status"] = np.random.choice(a=["completed", 
    "cancelled", "refunded"], 
    p=[0.92, 0.05, 0.03], 
    size=len(purchase_events))

    orders = purchase_events[["order_id", "customer_id", "session_id", 
                              "event_timestamp", "payment_method", 
                              "order_status"]].rename(columns={"event_timestamp": "order_timestamp"})

    order_items = purchase_events[["order_id", "product_id", "price"]].copy()

    order_items = order_items.rename(columns={"price": "unit_price"})

    order_items["quantity"] = np.random.choice(a=[1, 2, 3], 
    p=[0.80, 0.17, 0.03], 
    size=len(order_items))

    order_items["discount_pct"] = np.random.choice(
    a=[0, 0.05, 0.10, 0.15, 0.20], 
    p=[0.50, 0.20, 0.15, 0.10, 0.05], 
    size=len(order_items))

    order_items["line_total"] = order_items["quantity"] * order_items["unit_price"] * (1 - order_items["discount_pct"])

    order_totals = order_items.groupby("order_id", as_index=False)["line_total"].sum().rename(columns={"line_total": "total_amount"})

    orders = orders.merge(right=order_totals, how="left", on="order_id", validate="one_to_one")

    orders["total_amount"] = orders["total_amount"].round(2)
    order_items["unit_price"] = order_items["unit_price"].round(2)
    order_items["line_total"] = order_items["line_total"].round(2)

    return orders, order_items
    


# In[11]:


orders_base_table, order_items_base_table = create_order_data(events_base_table, product_base_table, seed=48)


# In[12]:


clean_dir = Path("funnel_data/clean")


# In[13]:


clean_dir.mkdir(parents=True, exist_ok=True)


# In[14]:


customer_base_table.to_csv(clean_dir / "customers.csv", index=False)


# In[15]:


product_base_table.to_csv(clean_dir / "products.csv", index=False)


# In[16]:


events_base_table.to_csv(clean_dir / "events.csv", index=False)


# In[17]:


orders_base_table.to_csv(clean_dir / "orders.csv", index=False)


# In[18]:


order_items_base_table.to_csv(clean_dir / "order_items.csv", index=False)


# In[19]:


list(clean_dir.iterdir())


# In[20]:


dirty_dir = Path("funnel_data/dirty")


# In[21]:


dirty_dir.mkdir(parents=True, exist_ok=True)


# In[22]:


customers_dirty = pd.read_csv("funnel_data/clean/customers.csv")
products_dirty = pd.read_csv("funnel_data/clean/products.csv")
events_dirty = pd.read_csv("funnel_data/clean/events.csv")
orders_dirty = pd.read_csv("funnel_data/clean/orders.csv")
order_items_dirty = pd.read_csv("funnel_data/clean/order_items.csv")


# In[23]:


dirty_tables = {
    "customers": customers_dirty, 
    "products": products_dirty, 
    "events": events_dirty, 
    "orders": orders_dirty, 
    "order_items": order_items_dirty
}
for name, df in dirty_tables.items():
    print(f"{name}: {df.shape}")


# In[24]:


for name in ["events", "orders", "order_items"]:
    df = dirty_tables[name]

    n_duplicates = max(1, int(len(df) * 0.001))

    duplicate_rows = df.sample(
        n=n_duplicates,
        random_state=42
    )

    df_dirty = pd.concat(
        [df, duplicate_rows],
        ignore_index=True
    )

    dirty_tables[name] = df_dirty



# In[25]:


for name in ["events", "orders", "order_items"]:
    df = dirty_tables[name]
    print(f"{name}: {df.duplicated().sum()} exact duplicate rows")


# In[26]:


rng = np.random.default_rng(seed=42)

missingness_plan = {
    "products": {"brand": 0.03},
    "events": {"traffic_source": 0.01, "device": 0.005},
    "orders": {"payment_method": 0.01},
}

for table_name, columns in missingness_plan.items():
    df = dirty_tables[table_name]

    for column, rate in columns.items():
        n_missing = int(len(df) * rate)
        row_indices = rng.choice(df.index, size=n_missing, replace=False)
        df.loc[row_indices, column] = np.nan

        print(
            f"{table_name}.{column}: "
            f"introduced {n_missing:,} missing values"
        )


# In[27]:


for name in ["products", "events", "orders"]:
    print(f"\n{name}:")
    print(dirty_tables[name].isna().sum())


# In[28]:


text_variations = {
    "products": {
        "category": {
            "Apparel": " apparel ",
            "Footwear": "FOOTWEAR",
            "Accessories": "accessories",
        },
        "brand": {
            "Nike": " NIKE ",
            "Adidas": "adidas",
            "Puma": "PUMA",
        },
    },
    "events": {
        "device": {
            "mobile": "Mobile",
            "desktop": " DESKTOP ",
            "tablet": "TABLET",
        },
        "traffic_source": {
            "Organic Search": "organic search",
            "Paid Search": " Paid Search ",
            "Social": "SOCIAL",
            "Email": "email",
        },
    },
}

for table_name, columns in text_variations.items():
    df = dirty_tables[table_name]

    for column, replacements in columns.items():
        for original, replacement in replacements.items():
            mask = df[column].eq(original)
            df.loc[mask, column] = replacement

            print(
                f"{table_name}.{column}: "
                f"{mask.sum():,} values changed from "
                f"{original!r} to {replacement!r}"
            )


# In[29]:


print("Product price range:")
print(dirty_tables["products"]["price"].describe())

print("\nEvent types:")
print(dirty_tables["events"]["event_type"].value_counts(dropna=False))

print("\nOrder statuses:")
print(dirty_tables["orders"]["order_status"].value_counts(dropna=False))


# In[30]:


products = dirty_tables["products"]

products.loc[products.index[:3], "price"] = [-10, 0, -5]


events = dirty_tables["events"]

events.loc[events.index[:5], "event_type"] = [
    "view_item",
    "add_to_basket",
    "click",
    "purchase_complete",
    "unknown",
]


orders = dirty_tables["orders"]

orders.loc[orders.index[:4], "order_status"] = [
    "pending",
    "processing",
    "failed",
    "shipped",
]


# In[31]:


print(dirty_tables["products"]["price"].sort_values().head(5))

print("\nEvent types:")
print(dirty_tables["events"]["event_type"].value_counts())

print("\nOrder statuses:")
print(dirty_tables["orders"]["order_status"].value_counts())


# In[32]:


products = dirty_tables["products"]

products.loc[products.index[3:5], "price"] = [
    "unknown",
    "N/A",
]


events = dirty_tables["events"]

events.loc[events.index[5], "event_timestamp"] = "not_a_timestamp"


orders = dirty_tables["orders"]

orders.loc[orders.index[4:6], "total_amount"] = [
    "not available",
    "unknown",
]


# In[33]:


for table_name, column in [
    ("products", "price"),
    ("events", "event_timestamp"),
    ("orders", "total_amount"),
]:
    df = dirty_tables[table_name]

    print(f"\n{table_name}.{column}")
    print("dtype:", df[column].dtype)
    print("Sample values:")
    print(df[column].head(8))


# In[34]:


for table_name, df in dirty_tables.items():
    file_path = dirty_dir / f"{table_name}.csv"
    df.to_csv(file_path, index=False)

    print(
        f"Saved {table_name}: "
        f"{len(df):,} rows → {file_path}"
    )


# In[ ]:





# In[ ]:




