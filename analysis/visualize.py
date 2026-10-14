import pandas as pd
import matplotlib.pyplot as plt
import os


# LOAD DATA
orders = pd.read_csv("orders.csv")
customers = pd.read_csv("customers.csv")
products = pd.read_csv("products.csv")


# CLEAN PAYMENT METHODS
orders["payment_method"] = (
    orders["payment_method"]
    .str.strip()
    .str.upper()
)


# REMOVE DUPLICATES
orders_clean = orders.drop_duplicates(
    subset=[
        "customer_id",
        "product_id",
        "order_date",
        "quantity",
        "discount_pct",
        "payment_method",
        "rating",
        "returned"
    ],
    keep="first"
).copy()


# MERGE DATA
merged = (
    orders_clean
    .merge(products, on="product_id", how="left")
    .merge(customers, on="customer_id", how="left")
)


# CALCULATE ORDER VALUE
merged["order_value"] = (
    merged["quantity"]
    * merged["price"]
    * (1 - merged["discount_pct"].fillna(0) / 100)
)


# Create output folder
os.makedirs("visualizations", exist_ok=True)


# VISUALIZATION 1 ===

# RETURN RATE BY PAYMENT METHOD
return_analysis = (
    merged.groupby("payment_method")["returned"]
    .mean()
    .mul(100)
    .sort_values(ascending=False)
)

methods = return_analysis.index.tolist()
rates = return_analysis.values


# Create figure
fig, ax = plt.subplots(figsize=(10, 6))

# Colors: highest return rate highlighted
colors = []

for i, method in enumerate(methods):
    if i == 0:
        colors.append("#E63946")
    else:
        colors.append("#457B9D")


# Horizontal bars
bars = ax.barh(
    methods,
    rates,
    color=colors,
    height=0.55
)

# Highest rate on top
ax.invert_yaxis()


# Add percentage labels
for bar, value in zip(bars, rates):
    ax.text(
        value + 0.8,
        bar.get_y() + bar.get_height() / 2,
        f"{value:.1f}%",
        va="center",
        fontsize=12,
        fontweight="bold"
    )


# Calculate comparison with CARD
highest_method = methods[0]
highest_rate = rates[0]

card_rate = return_analysis["CARD"]

ratio = highest_rate / card_rate

# Dynamic title
ax.set_title(
    f"{highest_method} Returns at {highest_rate:.1f}% — "
    f"{ratio:.1f}× CARD",
    fontsize=18,
    fontweight="bold",
    pad=20
)

ax.set_xlabel(
    "Return Rate (%)",
    fontsize=12,
    fontweight="bold"
)

ax.set_ylabel(
    "Payment Method",
    fontsize=12,
    fontweight="bold"
)


# Subtle grid
ax.grid(
    axis="x",
    linestyle="--",
    alpha=0.25
)

ax.set_axisbelow(True)


# Remove unnecessary borders
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)


# Add small insight
ax.text(
    0,
    -0.18,
    "Higher return rate indicates greater order-return risk",
    transform=ax.transAxes,
    fontsize=10,
    alpha=0.65
)

plt.tight_layout()

plt.savefig(
    "visualizations/return_rate_by_payment.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# VISUALIZATION 2 ===

# OUTLIER-CORRECTED MONTHLY REVENUE

# Remove quantity outliers from Task 6
merged_without_outliers = merged[
    ~merged["order_id"].isin(["O0011", "O0098"])
].copy()


# Convert date
merged_without_outliers["order_date"] = pd.to_datetime(
    merged_without_outliers["order_date"]
)


# Create year-month
merged_without_outliers["year_month"] = (
    merged_without_outliers["order_date"]
    .dt.to_period("M")
)


# Calculate monthly revenue
monthly_revenue = (
    merged_without_outliers
    .groupby("year_month")["order_value"]
    .sum()
)


# Find actual peak
peak_month = monthly_revenue.idxmax()
peak_revenue = monthly_revenue.max()


# Convert labels to strings
months = monthly_revenue.index.astype(str)


# CREATE REVENUE CHART

fig, ax = plt.subplots(figsize=(11, 6))


# Main revenue line
ax.plot(
    months,
    monthly_revenue.values,
    marker="o",
    markersize=8,
    linewidth=3,
    color="#2A9D8F"
)


# Filled area under the line
ax.fill_between(
    range(len(months)),
    monthly_revenue.values,
    alpha=0.12,
    color="#2A9D8F"
)

# Adding peak month text
peak_position = monthly_revenue_without_outliers.index.get_loc(monthly_revenue_without_outliers.idxmax())
peak_revenue = float(monthly_revenue_without_outliers.max())
ax.annotate(
    "PEAK MONTH",
    xy=(peak_position, peak_revenue),
    xytext=(0, 21),
    textcoords="offset points",
    ha="center",
    fontsize=10,
    fontweight="bold",
    color="#E63946"
)

# Highlight peak point
peak_position = list(monthly_revenue.index).index(peak_month)

ax.scatter(
    peak_position,
    peak_revenue,
    s=100,
    color="#E63946",
    zorder=5
)


# Add revenue values above every point
for x, y in enumerate(monthly_revenue.values):
    ax.text(
        x,
        y + monthly_revenue.max() * 0.025,
        f"₹{y:,.0f}",
        ha="center",
        fontsize=9,
        fontweight="bold"
    )


# Dynamic title
ax.set_title(
    f"Monthly Revenue Trend — Actual Peak Month: {peak_month}",
    fontsize=18,
    fontweight="bold",
    pad=20
)

ax.set_xlabel(
    "Month",
    fontsize=12,
    fontweight="bold"
)

ax.set_ylabel(
    "Revenue (₹)",
    fontsize=12,
    fontweight="bold"
)


# Grid
ax.grid(
    axis="y",
    linestyle="--",
    alpha=0.25
)

ax.set_axisbelow(True)


# Remove unnecessary borders
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)


# Rotate month labels
plt.xticks(rotation=0)

plt.tight_layout()

plt.savefig(
    "visualizations/monthly_revenue_trend.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()
                                                    
# FINAL OUTPUT

print("Visualizations created successfully.")
print("Peak month:", peak_month)
print("Peak revenue:", round(peak_revenue, 2))
print("Files saved in: visualizations/")
