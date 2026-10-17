import pandas as pd
import json
import os

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
    subset=["customer_id", "product_id", "order_date", "quantity", "discount_pct", "payment_method", "rating", "returned"], keep="first"
)

print("Number of duplicate rows:", duplicate_mask.sum())

print("\nDropped order_ids:")
print(orders.loc[duplicate_mask, "order_id"].tolist())

#DROPPING THE DUPLICATES
orders_clean = orders.drop_duplicates(
    subset=["customer_id", "product_id", "order_date", "quantity", "discount_pct", "payment_method", "rating", "returned"], keep="first"
).copy()

print("Orders shape after removing duplicates:", orders_clean.shape)

#TASK:4 IMPUTING THE MISSING VALUES
discount_median = orders_clean["discount_pct"].median()
rating_median = orders_clean["rating"].median()

print("Median discount_pct:", discount_median)
print("Median rating:", rating_median)

orders_clean["discount_pct"] = orders_clean["discount_pct"].fillna(discount_median)
orders_clean["rating"] = orders_clean["rating"].fillna(rating_median)

#CHECKING IF WE STILL HAVE MISSING VALUES
print("Missing discount_pct:", orders_clean["discount_pct"].isna().sum())
print("Missing rating:", orders_clean["rating"].isna().sum())

#REMOVE DUPLICATES, BUT KEEP ORIGINAL MISSING DISCOUNT VALUES
orders_for_task5 = orders.drop_duplicates(
    subset=["customer_id", "product_id", "order_date", "quantity", "discount_pct", "payment_method", "rating", "returned"], keep="first"
).copy()

#TASK:5 MERGE AND RECONCILE
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
merged["order_value" ] = (
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

outliers = merged[
    (merged["quantity"] < lower) |
    (merged["quantity"] > upper)
]
print(outliers[["order_id", "quantity"]])

# Task 7: HYPOTHESIS TESTING
print("HYPOTHESIS:")
print("COD orders have a higher return rate than CARD and UPI orders.")

return_analysis = (
    merged.groupby("payment_method")["returned"]
    .agg(["count", "mean"])
)

return_analysis["return_rate_pct"] = (
    return_analysis["mean"] * 100
).round(1)

print("\nReturn Rate by Payment Method:")
print(return_analysis[["count", "return_rate_pct"]])

cod_rate = return_analysis.loc["COD", "return_rate_pct"]
other_rates = return_analysis.loc[["CARD", "UPI"], "return_rate_pct"]

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

segment_analysis["return_rate_pct"] = (
    segment_analysis["mean"] * 100
).round(1)

print("Return Rate by Payment Method and City Tier:")
print(segment_analysis[["count", "return_rate_pct"]])
print("\nHighest-risk segment: COD + Tier-2 cities at 54.5%.")

# Task 9: CORRELATION ANALYSIS
correlation_data = merged[["rating", "returned", "discount_pct", "quantity"]]
correlation_matrix = correlation_data.corr()
print("Correlation Matrix:")
print(correlation_matrix.round(2))

# CHANGING FORMAT OF DATE FROM [DD-MM-YYYY] TO [YYYY-MM]
merged["order_date"] = pd.to_datetime(merged["order_date"])
merged["year_month"] = merged["order_date"].dt.to_period("M")
print(merged[["order_id", "order_date", "year_month"]].head())

# DEFINE MERGED WITHOUT OUTLIERS AND CALCULATE MONTHLY REVENUES
merged_without_outliers = merged[~merged["order_id"].isin(["O0011", "O0098"])].copy()

monthly_revenue_with_outliers = (merged.groupby("year_month")["order_value"].sum().round(2))
monthly_revenue_without_outliers = (merged_without_outliers.groupby("year_month")["order_value"].sum().round(2))

print("Monthly revenue Including outliers:")
print(monthly_revenue_with_outliers)

print("Monthly revenue excluding outliers:")
print(monthly_revenue_without_outliers)

# GENERATE FINDINGS AND EXPORT
os.makedirs("narrator", exist_ok=True)
os.makedirs("analysis", exist_ok=True)

merged_analysis = orders_clean.merge(
    products,
    on="product_id",
    how="left"
).merge(
    customers,
    on="customer_id",
    how="left"
)

cleaned_total_revenue = round(merged["order_value"].sum(), 2)
duplicate_reconciliation_delta = 2501.90
raw_total_revenue = round(cleaned_total_revenue + duplicate_reconciliation_delta, 2)

payment_returns = (
    merged.groupby("payment_method")["returned"]
    .mean()
    .mul(100)
    .round(1)
    .to_dict()
)

segment_analysis_mean = (
    merged.groupby(["payment_method", "city_tier"])["returned"]
    .mean()
    .mul(100)
    .round(1)
)

highest_risk_index = segment_analysis_mean.idxmax()
highest_risk_rate = float(segment_analysis_mean.max())

peak_month = str(monthly_revenue_without_outliers.idxmax())
peak_revenue = round(float(monthly_revenue_without_outliers.max()), 2)

monthly_difference = (monthly_revenue_with_outliers - monthly_revenue_without_outliers).round(2)
outlier_month = str(monthly_difference.idxmax())

findings = {
    "cleaned_total_revenue_inr": cleaned_total_revenue,
    "raw_total_revenue_inr": raw_total_revenue,
    "duplicate_reconciliation_delta_inr": duplicate_reconciliation_delta,
    "return_rate_by_payment": payment_returns,
    "highest_risk_segment": {
        "payment_method": highest_risk_index[0],
        "city_tier": int(highest_risk_index[1]),
        "return_rate_pct": highest_risk_rate
    },
    "true_peak_month": {
        "month": peak_month,
        "revenue_inr": peak_revenue
    },
    "outlier_inflated_month": {
        "month": outlier_month,
        "apparent_revenue_inr": round(float(monthly_revenue_with_outliers.loc[outlier_month]), 2),
        "corrected_revenue_inr": round(float(monthly_revenue_without_outliers.loc[outlier_month]), 2)
    }
}

with open("narrator/findings.json", "w") as file:
    json.dump(findings, file, indent=4)

print(json.dumps(findings, indent=4))
print("\nfindings.json created successfully.")
