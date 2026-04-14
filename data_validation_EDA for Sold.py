import pandas as pd
import matplotlib.pyplot as plt

sold = pd.read_csv("filtered/CRMLSSold_Residential.csv")

sold.shape
print(f'Number of rows: {sold.shape[0]}, Number of columns: {sold.shape[1]}')

sold.info()

sold.dtypes

sold.head()

sold['PropertyType'].value_counts(normalize=True)

property_types = sold['PropertyType'].unique()
print("Unique Property Types:")
print(property_types)

property_type_counts = sold['PropertyType'].value_counts()
print("\nProperty Type Counts:")
print(property_type_counts)

sold= sold[sold['PropertyType'] == 'Residential'].copy()

print("\nFiltered dataset shape:", sold.shape)

null_counts = sold.isnull().sum()
null_pct = sold.isnull().mean() * 100

null_summary = pd.DataFrame({
    "null_count": null_counts,
    "null_percentage": null_pct
}).sort_values(by="null_percentage", ascending=False)

print("\nNull Summary Table:")
print(null_summary)

high_null_cols = null_summary[null_summary["null_percentage"] > 90]

print("\nColumns with >90% missing values:")
print(high_null_cols)

def numeric_summary(df, col):
    return {
        "min": df[col].min(),
        "max": df[col].max(),
        "mean": df[col].mean(),
        "median": df[col].median(),
        "p01": df[col].quantile(0.01),
        "p05": df[col].quantile(0.05),
        "p25": df[col].quantile(0.25),
        "p50": df[col].quantile(0.50),
        "p75": df[col].quantile(0.75),
        "p95": df[col].quantile(0.95),
        "p99": df[col].quantile(0.99)
    }

numeric_cols = [
    "ClosePrice",
    "ListPrice",
    "OriginalListPrice",
    "LivingArea",
    "LotSizeAcres",
    "BedroomsTotal",
    "BathroomsTotalInteger",
    "DaysOnMarket",
    "YearBuilt"
]
cols_to_drop = high_null_cols.index.tolist()
sold = sold.drop(columns=cols_to_drop)
print("Dropped columns:", cols_to_drop)

for col in numeric_cols:
    sold[col] = pd.to_numeric(sold[col], errors='coerce')
percentile_summary = sold[numeric_cols].describe(
    percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]
)

# Histograms for numeric features
sold[numeric_cols].hist(bins=30, figsize=(16, 10))
plt.suptitle("Histograms of Key Numeric Features", fontsize=16)
plt.tight_layout()
plt.show()

print("\nPercentile Summary:")
print(percentile_summary)

# Boxplots for numeric features
for col in numeric_cols:
    plt.figure(figsize=(6, 4))
    sold.boxplot(column=col)
    plt.title(f"Boxplot: {col}")
    plt.show()

# outlier detection (IQR method)
def detect_outliers_iqr(df, col):
    q1 = df[col].quantile(0.25)
    q3 = df[col].quantile(0.75)
    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]

    return outliers, lower_bound, upper_bound


outlier_report = {}

print("\nOutlier Summary:")
for col in numeric_cols:
    outliers, low, high = detect_outliers_iqr(sold, col)

    outlier_report[col] = {
        "num_outliers": len(outliers),
        "lower_bound": low,
        "upper_bound": high
    }

    print(f"{col}: {len(outliers)} outliers | bounds=({low:.2f}, {high:.2f})")


cols_to_analyze = ["ClosePrice", "LivingArea", "DaysOnMarket"]

numeric_report = pd.DataFrame({
    col: numeric_summary(sold, col)
    for col in cols_to_analyze
}).T

print("\nNumeric Distribution Summary:")
print(numeric_report)

print("\nProperty Type Distribution:")
property_share = sold['PropertyType'].value_counts(normalize=True) * 100
print(property_share)

print("\nWhat are the median and average close prices?")
price_stats = sold['ClosePrice'].agg(['mean', 'median'])
print(price_stats)

print("\nWhat does the Days on Market distribution look like?")
sold['DaysOnMarket'].describe()
sold['DaysOnMarket'].hist(bins=50)
plt.title("Days on Market Distribution")
plt.show()

print("\nWhat percentage of homes sold above vs. below list price?")
sold['above_list'] = sold['ClosePrice'] > sold['ListPrice']
above_below_pct = sold['above_list'].value_counts(normalize=True) * 100
print(above_below_pct)

print("\nWhich counties have the highest median prices?")
county_prices = (
    sold.groupby('CountyOrParish')['ClosePrice']
    .median()
    .sort_values(ascending=False)
)
print(county_prices.head(10))

output_file = "filtered/sold_residential_filtered.csv"
sold.to_csv(output_file, index=False)

print(f"\nFiltered dataset saved to: {output_file}")