#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import datetime as dt
from pathlib import Path


# In[2]:


dirty_dir = Path("funnel_data/dirty")
clean_dir = Path("funnel_data/cleaned")
clean_dir.mkdir(parents=True, exist_ok=True)

customers = pd.read_csv(dirty_dir / "customers.csv")
products = pd.read_csv(dirty_dir / "products.csv")
events = pd.read_csv(dirty_dir / "events.csv")
orders = pd.read_csv(dirty_dir / "orders.csv")
order_items = pd.read_csv(dirty_dir / "order_items.csv")

tables = {
    "customers": customers,
    "products": products,
    "events": events,
    "orders": orders,
    "order_items": order_items,
}


# In[3]:


for name, df in tables.items():
    print(f"{name}: {df.shape}")
    print(f"{name}: {df.duplicated().sum():,} exact duplicate rows")


# In[4]:


for name in ["events", "orders", "order_items"]:
    before = len(tables[name])

    tables[name] = tables[name].drop_duplicates().copy()

    after = len(tables[name])

    print(f"{name}: removed {before - after:,} rows "
            f"({before:,} -> {after:,})")
for name, df in tables.items():
    print(f"{name}: {df.duplicated().sum():,} exact duplicates")


# In[5]:


for name, df in tables.items():
    print(f"\n--- {name} ---")
    print(df.dtypes)


# In[6]:


tables["customers"]["signup_date"] = pd.to_datetime(tables["customers"]["signup_date"], errors="coerce")


# In[7]:


tables["events"]["event_timestamp"] = pd.to_datetime(tables["events"]["event_timestamp"], errors="coerce")


# In[8]:


tables["orders"]["order_timestamp"] = pd.to_datetime(tables["orders"]["order_timestamp"], errors="coerce")


# In[9]:


timestamp_columns = {
    "customers": ["signup_date"],
    "events": ["event_timestamp"],
    "orders": ["order_timestamp"],
}

for table_name, columns in timestamp_columns.items():
    for column in columns:
        tables[table_name][column] = (
            tables[table_name][column].dt.round("us")
        )


# In[10]:


numeric_columns = {"products": ["price"], 
                   "events": ["price"], 
                   "orders": ["total_amount"], 
                   "order_items": ["unit_price", "quantity", 
                                   "discount_pct", "line_total"]}

for table_name, columns in numeric_columns.items():
    for column in columns:
        tables[table_name][column] = pd.to_numeric(tables[table_name][column], errors="coerce")


# In[11]:


for name, df in tables.items():
    print(f"\n--- {name} ---")
    print(df.dtypes)


# In[12]:


text_columns = {
    "products": ["category", "subcategory", "brand"],
    "events": [
        "event_type",
        "device",
        "traffic_source",
        "category",
        "subcategory",
        "brand",
    ],
    "orders": ["payment_method", "order_status"],
}

for table_name, columns in text_columns.items():
    for column in columns:
        tables[table_name][column] = tables[table_name][column].str.strip().str.lower()


# In[13]:


valid_event_types = {
    "view",
    "add_to_cart",
    "checkout",
    "purchase",
}

valid_order_statuses = {
    "completed",
    "cancelled",
    "refunded",
}


# In[14]:


invalid_events = tables["events"][~tables["events"]["event_type"].isin(valid_event_types)]


# In[15]:


invalid_orders = tables["orders"][~tables["orders"]["order_status"].isin(valid_order_statuses)]


# In[16]:


print("Unexpected event types:")
print(invalid_events["event_type"].value_counts(dropna=False))

print("\nUnexpected order statuses:")
print(invalid_orders["order_status"].value_counts(dropna=False))


# In[17]:


tables["events"]["event_type"] = tables["events"]["event_type"].where(tables["events"]["event_type"].isin(valid_event_types), pd.NA)


# In[18]:


tables["orders"]["order_status"] = tables["orders"]["order_status"].where(tables["orders"]["order_status"].isin(valid_order_statuses), pd.NA)


# In[19]:


invalid_product_prices = tables["products"]["price"] <= 0
print("Non-positive product prices:", invalid_product_prices.sum())

tables["products"].loc[invalid_product_prices, "price"] = pd.NA


# In[20]:


print("Event prices below zero:", (tables["events"]["price"] < 0).sum())
print("Order totals below zero:", (tables["orders"]["total_amount"] < 0).sum())
print("Unit prices below zero:", (tables["order_items"]["unit_price"] < 0).sum())
print("Quantities at or below zero:", (tables["order_items"]["quantity"] <= 0).sum())
print("Discounts below zero:", (tables["order_items"]["discount_pct"] < 0).sum())
print("Discounts above 100%:", (tables["order_items"]["discount_pct"] > 1).sum())
print("Line totals below zero:", (tables["order_items"]["line_total"] < 0).sum())


# In[21]:


for name, df in tables.items():
    print(f"\n--- {name} ---")
    print(df.isna().sum()[df.isna().sum() > 0])


# In[22]:


tables["orders"].loc[tables["orders"]["total_amount"].isna(), ["order_id", "customer_id", "total_amount", "order_status"]]


# In[23]:


affected_order_ids = tables["orders"].loc[
    tables["orders"]["total_amount"].isna(),
    "order_id"
]

tables["order_items"].loc[
    tables["order_items"]["order_id"].isin(affected_order_ids)
].sort_values(["order_id", "product_id"])


# In[24]:


reconstructed_totals = tables["order_items"].groupby("order_id")["line_total"].sum()


missing_total_mask = tables["orders"]["total_amount"].isna()

tables["orders"].loc[missing_total_mask, "total_amount"] = tables["orders"].loc[missing_total_mask, "order_id"].map(reconstructed_totals)


# In[25]:


print("Missing order totals:", tables["orders"]["total_amount"].isna().sum())

tables["orders"].loc[
    tables["orders"]["order_id"].isin(affected_order_ids),
    ["order_id", "total_amount"]
]


# In[26]:


for name, df in tables.items():
    missing = df.isna().sum()
    missing = missing[missing > 0]

    print(f"\n--- {name} ---")
    print(missing if not missing.empty else "No missing values")


# In[ ]:





# In[27]:


primary_keys = {
    "customers": "customer_id",
    "products": "product_id",
    "events": "event_id",
    "orders": "order_id",
    "order_items": None,
}

for name, key in primary_keys.items():
    if key is None:
        continue

    df = tables[name]

    print(f"\n--- {name} ---")
    print(f"Missing {key}: {df[key].isna().sum()}")
    print(f"Duplicate {key} rows: {df[key].duplicated().sum()}")
    print(f"Unique {key} values: {df[key].nunique()}")


# In[28]:


duplicate_events = tables["events"][
    tables["events"]["event_id"].duplicated(keep=False)
].sort_values("event_id")

duplicate_events.head(20)


# In[29]:


duplicate_events = tables["events"][
    tables["events"]["event_id"].duplicated(keep=False)
].copy()

core_columns = [
    "customer_id",
    "session_id",
    "event_timestamp",
    "event_type",
    "product_id",
    "price",
]

core_variation = (
    duplicate_events
    .groupby("event_id")[core_columns]
    .nunique(dropna=False)
)

print("Duplicate event IDs:", len(core_variation))
print(
    "IDs with conflicting core details:",
    (core_variation > 1).any(axis=1).sum()
)


# In[30]:


before = len(tables["events"])

tables["events"] = tables["events"].assign(_missing_count=tables["events"].isna().sum(axis=1)).sort_values("_missing_count").drop_duplicates(subset="event_id", keep="first").drop(columns="_missing_count").copy()


after = len(tables["events"])

print(f"Rows removed: {before - after:,}")
print(f"Rows remaining: {after:,}")
print(
    "Duplicate event IDs remaining:",
    tables["events"]["event_id"].duplicated().sum()
)


# In[31]:


duplicate_orders = tables["orders"][
    tables["orders"]["order_id"].duplicated(keep=False)
].sort_values("order_id")

duplicate_orders


# In[32]:


before = len(tables["orders"])

tables["orders"] = tables["orders"].assign(
        _missing_count=tables["orders"].isna().sum(axis=1)
    ).sort_values("_missing_count").drop_duplicates(subset="order_id", keep="first").drop(columns="_missing_count").copy()


after = len(tables["orders"])

print(f"Rows removed: {before - after:,}")
print(f"Rows remaining: {after:,}")
print(
    "Duplicate order IDs remaining:",
    tables["orders"]["order_id"].duplicated().sum()
)


# In[33]:


relationships = [
    ("events.customer_id", tables["events"], "customer_id",
     tables["customers"], "customer_id"),
    ("events.product_id", tables["events"], "product_id",
     tables["products"], "product_id"),
    ("orders.customer_id", tables["orders"], "customer_id",
     tables["customers"], "customer_id"),
    ("orders.session_id", tables["orders"], "session_id",
     tables["events"], "session_id"),
    ("order_items.order_id", tables["order_items"], "order_id",
     tables["orders"], "order_id"),
    ("order_items.product_id", tables["order_items"], "product_id",
     tables["products"], "product_id"),
]

for label, child_df, child_col, parent_df, parent_col in relationships:
    unmatched = ~child_df[child_col].isin(parent_df[parent_col])
    print(f"{label}: {unmatched.sum():,} unmatched rows")


# In[34]:


for name, df in tables.items():
    print(f"\n--- {name} ---")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print(f"Exact duplicate rows: {df.duplicated().sum():,}")
    print(f"Total missing values: {df.isna().sum().sum():,}")


# In[35]:


for name, df in tables.items():
    output_path = clean_dir / f"{name}.csv"
    df.to_csv(output_path, index=False)
    print(f"Saved {name}: {len(df):,} rows -> {output_path}")


# In[36]:


# Load cleaned data
DATA_DIR = Path("funnel_data/cleaned")

customers = pd.read_csv(DATA_DIR / "customers.csv")
products = pd.read_csv(DATA_DIR / "products.csv")
events = pd.read_csv(DATA_DIR / "events.csv")
orders = pd.read_csv(DATA_DIR / "orders.csv")
order_items = pd.read_csv(DATA_DIR / "order_items.csv")

# Restore data types
customers["signup_date"] = pd.to_datetime(
    customers["signup_date"], errors="coerce"
)
products["price"] = pd.to_numeric(products["price"], errors="coerce")
events["event_timestamp"] = pd.to_datetime(
    events["event_timestamp"], errors="coerce"
)
events["price"] = pd.to_numeric(events["price"], errors="coerce")
orders["order_timestamp"] = pd.to_datetime(
    orders["order_timestamp"], errors="coerce"
)
orders["total_amount"] = pd.to_numeric(
    orders["total_amount"], errors="coerce"
)

for col in ["unit_price", "discount_pct", "line_total"]:
    order_items[col] = pd.to_numeric(
        order_items[col], errors="coerce"
    )

# 1. Table-level checks
tables = {
    "customers": customers,
    "products": products,
    "events": events,
    "orders": orders,
    "order_items": order_items,
}

print("=== TABLE VALIDATION ===")

for name, df in tables.items():
    print(f"\n{name}")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print(f"Exact duplicate rows: {df.duplicated().sum():,}")
    print(f"Total missing values: {df.isna().sum().sum():,}")

    missing = df.isna().sum()
    if missing.any():
        print("Missing by column:")
        print(missing[missing > 0])


# 2. Primary-key checks
primary_keys = {
    "customers": (customers, "customer_id"),
    "products": (products, "product_id"),
    "events": (events, "event_id"),
    "orders": (orders, "order_id"),
}

print("\n=== PRIMARY KEY VALIDATION ===")

for name, (df, key) in primary_keys.items():
    print(
        f"{name}.{key}: "
        f"missing={df[key].isna().sum():,}, "
        f"duplicate rows={df[key].duplicated().sum():,}, "
        f"unique={df[key].nunique():,}"
    )


# 3. Foreign-key checks
foreign_keys = [
    ("events.customer_id", events, "customer_id", customers, "customer_id"),
    ("events.product_id", events, "product_id", products, "product_id"),
    ("orders.customer_id", orders, "customer_id", customers, "customer_id"),
    ("orders.session_id", orders, "session_id", events, "session_id"),
    ("order_items.order_id", order_items, "order_id", orders, "order_id"),
    ("order_items.product_id", order_items, "product_id", products, "product_id"),
]

print("\n=== FOREIGN KEY VALIDATION ===")

for label, child, child_col, parent, parent_col in foreign_keys:
    valid_values = set(parent[parent_col].dropna())
    unmatched = (
        child[child_col].notna()
        & ~child[child_col].isin(valid_values)
    ).sum()

    print(f"{label}: {unmatched:,} unmatched rows")


# 4. Allowed categorical values
print("\n=== CATEGORY VALIDATION ===")

valid_event_types = {"view", "add_to_cart", "checkout", "purchase"}
valid_order_statuses = {"completed", "cancelled"}
valid_payment_methods = {"credit_card", "paypal", "debit_card", "gift_card"}

print("\nUnexpected event types:")
print(
    events.loc[
        ~events["event_type"].isin(valid_event_types),
        "event_type"
    ].value_counts(dropna=False)
)

print("\nUnexpected order statuses:")
print(
    orders.loc[
        ~orders["order_status"].isin(valid_order_statuses),
        "order_status"
    ].value_counts(dropna=False)
)

print("\nUnexpected payment methods:")
print(
    orders.loc[
        orders["payment_method"].notna()
        & ~orders["payment_method"].isin(valid_payment_methods),
        "payment_method"
    ].value_counts(dropna=False)
)


# 5. Numeric and timestamp constraints
print("\n=== VALUE VALIDATION ===")

checks = {
    "Product prices below zero": (products["price"] < 0).sum(),
    "Event prices below zero": (events["price"] < 0).sum(),
    "Order totals below zero": (orders["total_amount"] < 0).sum(),
    "Unit prices below zero": (order_items["unit_price"] < 0).sum(),
    "Quantities at or below zero": (order_items["quantity"] <= 0).sum(),
    "Discounts below 0%": (order_items["discount_pct"] < 0).sum(),
    "Discounts above 100%": (order_items["discount_pct"] > 100).sum(),
    "Line totals below zero": (order_items["line_total"] < 0).sum(),
    "Unparseable event timestamps": events["event_timestamp"].isna().sum(),
    "Unparseable order timestamps": orders["order_timestamp"].isna().sum(),
}

for label, count in checks.items():
    print(f"{label}: {count:,}")


# 6. Reconcile order totals against order items
print("\n=== ORDER TOTAL RECONCILIATION ===")

item_totals = (
    order_items.groupby("order_id", as_index=False)["line_total"]
    .sum()
    .rename(columns={"line_total": "calculated_total"})
)

reconciliation = orders[["order_id", "total_amount"]].merge(
    item_totals,
    on="order_id",
    how="outer",
    indicator=True,
    validate="one_to_one",
)

reconciliation["difference"] = (
    reconciliation["total_amount"] - reconciliation["calculated_total"]
)

tolerance = 0.01

mismatches = reconciliation.loc[
    reconciliation["_merge"].ne("both")
    | reconciliation["difference"].abs().gt(tolerance)
]

print(f"Orders checked: {len(reconciliation):,}")
print(f"Orders with missing/multiple-side records or mismatched totals: {len(mismatches):,}")

if not mismatches.empty:
    print(mismatches.head(20).to_string(index=False))


# 7. Final summary
print("\n=== VALIDATION COMPLETE ===")


# In[ ]:




