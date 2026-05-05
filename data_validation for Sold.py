import pandas as pd

sold = pd.read_csv("/Users/li/Desktop/idx Exchange/filtered/CRMLSSold_Residential.csv")

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


for col in numeric_cols:
    sold[col] = pd.to_numeric(sold[col], errors='coerce')
percentile_summary = sold[numeric_cols].describe(
    percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]
)

output_file = "/Users/li/Desktop/idx Exchange/filtered/sold_residential_filtered.csv"
sold.to_csv(output_file, index=False)

# Week 4-5
date_cols = [
    "CloseDate",
    "PurchaseContractDate",
    "ListingContractDate",
    "ContractStatusChangeDate"
]

for col in date_cols:

    sold[col] = pd.to_datetime(sold[col], errors='coerce')

before_cols = len(sold.columns)
cols_to_drop = [
    "FireplacesTotal", "AboveGradeFinishedArea", "TaxAnnualAmount",
    "TaxYear", "ElementarySchoolDistrict", "BusinessType",
    "CoveredSpaces", "MiddleOrJuniorSchoolDistrict",
    "WaterfrontYN", "BasementYN", "BelowGradeFinishedArea",
    "BuilderName", "LotSizeDimensions",

    "BuyerAgentFirstName", "BuyerAgentLastName", "BuyerAgentMlsId",
    "CoBuyerAgentFirstName", "CoListAgentFirstName",
    "CoListAgentLastName", "ListAgentEmail",
    "ListAgentFirstName", "ListAgentLastName", "ListAgentFullName"
]


sold = sold.drop(columns=cols_to_drop)

after_cols = len(sold.columns)
print(f"Columns before drop: {before_cols}, Columns after drop: {after_cols}")




numeric_cols = [
    "ClosePrice",
    "LivingArea",
    "DaysOnMarket",
    "Bedrooms",
    "Bathrooms"
]

for col in numeric_cols:

    if col in sold.columns:

        sold[col] = pd.to_numeric(sold[col], errors='coerce')

# Filter out rows with invalid numeric values
before_rows = len(sold)
sold = sold[
    (sold["ClosePrice"] > 0) &
    (sold["LivingArea"] > 0) &
    (sold["DaysOnMarket"] >= 0) &
    (sold["BedroomsTotal"] >= 0) &
    (sold["BathroomsTotalInteger"] >= 0)

]
after_rows = len(sold)
print(f"Rows before filtering: {before_rows}, Rows after filtering: {after_rows}")


# Data Consistency Checks
# 1. Listing after Close (should NOT happen)
sold["listing_after_close_flag"] = (
    sold["ListingContractDate"] > sold["CloseDate"]
)

# 2. Purchase after Close
sold["purchase_after_close_flag"] = (
    sold["PurchaseContractDate"] > sold["CloseDate"]
)

# 3. Negative timeline
sold["negative_timeline_flag"] = (
    (sold["ListingContractDate"] > sold["PurchaseContractDate"]) |
    (sold["PurchaseContractDate"] > sold["CloseDate"])
)

print("Listing after close:", sold["listing_after_close_flag"].sum())
print("Purchase after close:", sold["purchase_after_close_flag"].sum())
print("Negative timeline:", sold["negative_timeline_flag"].sum())

print(f"Total rows: {len(sold)}")
print(f"Total columns: {len(sold.columns)}")

# Week 5
# Flag missing coordinates
sold["missing_coordinates_flag"] = (
    sold["Latitude"].isna() | sold["Longitude"].isna()
)

# Flag zero coordinates
sold["zero_coordinates_flag"] = (
    (sold["Latitude"] == 0) | (sold["Longitude"] == 0)
)

# Flag positive longitude (invalid for California)
sold["positive_longitude_flag"] = (
    sold["Longitude"] > 0
)

# Flag out-of-bounds coordinates (California roughly between lat 32-42 and long -125 to -114)
sold["out_of_bounds_flag"] = (
    (sold["Latitude"] < 32) | (sold["Latitude"] > 42) |
    (sold["Longitude"] < -125) | (sold["Longitude"] > -114)
)

print("Missing coordinates:", sold["missing_coordinates_flag"].sum())
print("Zero coordinates:", sold["zero_coordinates_flag"].sum())
print("Positive longitude:", sold["positive_longitude_flag"].sum())
print("Out-of-bounds coordinates:", sold["out_of_bounds_flag"].sum())

sold.to_csv("/Users/li/Desktop/idx Exchange/filtered/sold_final.csv", index=False)