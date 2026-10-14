import pandas as pd

# TASK:1 LOADING THE DATA
orders = pd.read_csv("orders.csv")
customers = pd.read_csv("customers.csv")
products = pd.read_csv("products.csv")

print("Orders shape:", orders.shape)
print("Customers shape:", customers.shape)
print("Products shape:", products.shape)

#CHECKING THE RAW VALUES BEFORE THE FIX.

print("Raw payment methods:")
print(orders["payment_method"].unique())

#TASK:2 STANDARDIZING THE PAYMENT METHOD CASING:

orders["payment_method"] = orders["payment_method"].str.strip().str.upper()

print("Payment methods after standardization:")
print(orders["payment_method"].unique())

print("\nPayment method counts:")
print(orders["payment_method"].value_counts())

#TASK:3 DETECTING THE DUPLICATES

duplicate_mask = orders.duplicated(
    subset=["customer_id", "product_id", "order_date", "quantity", "discount_pct", "payment_method", "rating", "returned"],keep="first")

print("Number of duplicate rows:", duplicate_mask.sum())

print("\nDropped order_ids:")
print(orders.loc[duplicate_mask, "order_id"].tolist())

#DROPPING THE DUPLICATES

orders_clean = orders.drop_duplicates(
    subset=["customer_id", "product_id", "order_date", "quantity", "discount_pct", "payment_method", "rating", "returned"], keep="first").copy()

print("Orders shape after removing duplicates:", orders_clean.shape)

#TASK:4 IMPUTING THE MISSING VALUES
#COMPUTING THE MISSING VALUES IN COLUMN discount_pct & rating AND FILLING IN THE TABLE

discount_median = orders_clean["discount_pct"].median()
rating_median = orders_clean["rating"].median()

print("Median discount_pct:", discount_median)
print("Median rating:", rating_median)

orders_clean["discount_pct"] = orders_clean["discount_pct"].fillna(
    discount_median
)

orders_clean["rating"] = orders_clean["rating"].fillna(
    rating_median
)

#CHECKING IF WE STILL HAVE MISSING VALUES

print("Missing discount_pct:", orders_clean["discount_pct"].isna().sum())
print("Missing rating:", orders_clean["rating"].isna().sum())

#REMOVE DUPLICATES, BUT KEEP ORIGINAL MISSING DISCOUNT VALUES

orders_for_task5 = orders.drop_duplicates(
    subset=["customer_id", "product_id", "order_date", "quantity", "discount_pct", "payment_method", "rating", "returned"],keep="first").copy()

#TASK:5 MERGE AND RECONCILE 
#MERGING

merged = orders_for_task5.merge(
    products,
    on="product_id",
    how="left"
).merge(
    customers,
    on="customer_id",
    how="left"
)

#CALCULATING ORDER VALUE

merged["order_value"] = (
    merged["quantity"]
    * merged["price"]
    * (1 - merged["discount_pct"].fillna(0) / 100)
)

print("Merged shape:", merged.shape)
print("Total order value:", round(merged["order_value"].sum(), 2))

#RECONCILIATION:

print(
    "Reconciliation: Part 1 had total revenue of ₹99,860.20, while "
    "the cleaned data has revenue of ₹97,358.30. The difference is "
    "₹2,501.90, which matches the combined order value of the 5 duplicate "
    "orders removed in Task 3 (O0176–O0180). Therefore, the difference "
    "is due to removing these duplicate orders, not because of discount "
    "or rating imputation."
)

#TASK:6 IQR OUTLIER DETECTION ON QUANTITY

Q1 = merged["quantity"].quantile(0.25)
Q3 = merged["quantity"].quantile(0.75)

IQR = Q3 - Q1

lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

print("Q1:", Q1)
print("Q3:", Q3)
print("IQR:", IQR)
print("Lower bound:", lower)
print("Upper bound:", upper)

#IDENTIFYING THE OUTLIER ROWS

outliers = merged[
    (merged["quantity"] < lower) |
    (merged["quantity"] > upper)
]

print(outliers[["order_id", "quantity"]])

# Task 7: HYPOTHESIS TESTING

print("HYPOTHESIS:")
print("COD orders have a higher return rate than CARD and UPI orders.")

# Calculate return rates by payment method

return_analysis = (
    merged.groupby("payment_method")["returned"]
    .agg(["count", "mean"])
)

# Convert return rates to percentages

return_analysis["return_rate_pct"] = (
    return_analysis["mean"] * 100
).round(1)

# Display results

print("\nReturn Rate by Payment Method:")
print(return_analysis[["count", "return_rate_pct"]])

# Verify the hypothesis

cod_rate = return_analysis.loc["COD", "return_rate_pct"]
other_rates = return_analysis.loc[
    ["CARD", "UPI"], "return_rate_pct"
]

if (cod_rate > other_rates).all():
    print("\nHypothesis: CONFIRMED")
    print("COD has the highest return rate.")
else:
    print("\nHypothesis: NOT CONFIRMED")

# Task 8: MULTI-LEVEL SEGMENTATION

segment_analysis = (
    merged
    .groupby(["payment_method", "city_tier"])["returned"]
    .agg(["count", "mean"])
)

# CONVERT RETURN RATE TO %
segment_analysis["return_rate_pct"] = (
    segment_analysis["mean"] * 100
).round(1)

print("Return Rate by Payment Method and City Tier:")
print(segment_analysis[["count", "return_rate_pct"]])
print("\nHighest-risk segment: COD + Tier-2 cities at 54.5%.")
print("This shows that COD return risk is not uniform across city tiers.")

# Task 9: CORRELATION ANALYSIS

correlation_data = merged[
    ["rating", "returned", "discount_pct", "quantity"]
]

correlation_matrix = correlation_data.corr()

print("Correlation Matrix:")
print(correlation_matrix.round(2))

print("\nCorrelation Strength by Pair:")

print("Rating vs Returned: -0.10 → Negligible")
print("Rating vs Discount: 0.06 → Negligible")
print("Rating vs Quantity: -0.10 → Negligible")
print("Returned vs Discount: -0.12 → Negligible")
print("Returned vs Quantity: 0.04 → Negligible")
print("Discount vs Quantity: -0.18 → Negligible")

print("\nHypothesis: Higher discounts reduce returns")
print("Result: BUSTED")
print(
    "The correlation between discount_pct and returned is negligible "
    "(-0.12), so the data does not show a meaningful relationship "
    "between higher discounts and lower returns."
)

#CHANGING FORMAT OF DATE FROM[DD-MM-YYYY] TO [YYYY-MM]

merged["order_date"] = pd.to_datetime(merged["order_date"])

merged["year_month"] = merged["order_date"].dt.to_period("M")

print(merged[["order_id", "order_date", "year_month"]].head())

#CALCULATING MONTHLY REVENUE EXCLUDING THE 2 OUTLIERS AND STATING THE REASON OF THE OUTLIER

monthly_revenue_without_outliers = (merged_without_outliers.groupby("year_month")["order_value"].sum().round(2))

print("Monthly revenue Including outliers:")
print(monthly_revenue_with_outliers)

print("Monthly revenue excluding outliers:")
print(monthly_revenue_without_outliers)

print("\nCONCLUSION:")
print("Including the two [Task 6] outlier orders, January 2026 appears to be the highest month with an order value of 29582.10.")
print("However, January's higher total is due to the two unusually large bulk orders recorded that month.")
print("After excluding these outliers, March 2026 becomes the highest month with an order value of 20318.90.")
print("Therefore, January's higher total is misleading due to the two bulk orders, while March is the actual peak month after excluding them.")


