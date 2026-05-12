import pandas as pd
import numpy as np

def create_segment_summary(df, group_cols, top_n=None):
    """
    Create summary statistics for selected grouping columns.
    Parameters
    ----------
    df : pandas.DataFrame
    group_cols : str or list
        Column(s) used for grouping.
    top_n : int, optional
        Keep only the top N groups by transaction count.
    Returns
    -------
    pandas.DataFrame
    """

    if isinstance(group_cols, str):
        group_cols = [group_cols]
    # Aggregate statistics
    summary = (
        df.groupby(group_cols)
          .agg(
              Transactions=('ClosePrice', 'count'),
              MedianClosePrice=('ClosePrice', 'median'),
              AvgClosePrice=('ClosePrice', 'mean'),
              MedianPricePerSqFt=('PricePerSqFt', 'median'),
              AvgPricePerSqFt=('PricePerSqFt', 'mean'),
              MedianPriceRatio=('PriceRatio', 'median'),
              AvgPriceRatio=('PriceRatio', 'mean'),
              MedianDaysOnMarket=('DaysOnMarket_Clean', 'median'),
              AvgDaysOnMarket=('DaysOnMarket_Clean', 'mean'),
              MedianListingToContract=('ListingToContractDays', 'median'),
              AvgListingToContract=('ListingToContractDays', 'mean'),
              MedianContractToClose=('ContractToCloseDays', 'median'),
              AvgContractToClose=('ContractToCloseDays', 'mean')
          )
          .reset_index()
    )

    # Sort by transaction volume
    summary = summary.sort_values('Transactions', ascending=False)

    # Keep only top N groups if specified
    if top_n:
        summary = summary.head(top_n)

    # Round numeric columns
    numeric_cols = summary.select_dtypes(include=[np.number]).columns
    summary[numeric_cols] = summary[numeric_cols].round(2)
    return summary

listing = pd.read_csv("/Users/li/Desktop/idx Exchange/filtered/CRMLSListing_Residential.csv")

listing['PropertyType'].value_counts(normalize=True)

property_types = listing['PropertyType'].unique()
print("Unique Property Types:")
print(property_types)

property_type_counts = listing['PropertyType'].value_counts()
print("\nProperty Type Counts:")
print(property_type_counts)

listing= listing[listing['PropertyType'] == 'Residential'].copy()

null_counts = listing.isnull().sum()
null_pct = listing.isnull().mean() * 100

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
    listing[col] = pd.to_numeric(listing[col], errors='coerce')
percentile_summary = listing[numeric_cols].describe(
    percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]
)

output_file = "/Users/li/Desktop/idx Exchange/filtered/listing_residential_filtered.csv"
listing.to_csv(output_file, index=False)

date_cols = [
    "CloseDate",
    "PurchaseContractDate",
    "ListingContractDate",
    "ContractStatusChangeDate"
]

for col in date_cols:

    listing[col] = pd.to_datetime(listing[col], errors='coerce')

before_cols = len(listing.columns)
cols_to_drop = [
    "FireplacesTotal", "AboveGradeFinishedArea", "TaxAnnualAmount",
    "TaxYear", "ElementarySchoolDistrict", "BusinessType",
    "CoveredSpaces", "MiddleOrJuniorSchoolDistrict",
    "BelowGradeFinishedArea", "BuildingAreaTotal",
    "BuilderName", "LotSizeDimensions",

    "BuyerAgentFirstName", "BuyerAgentLastName", "BuyerAgentMlsId",
    "CoBuyerAgentFirstName", "CoListAgentFirstName",
    "CoListAgentLastName", "ListAgentEmail",
    "ListAgentFirstName", "ListAgentLastName", "ListAgentFullName"
]


listing = listing.drop(columns=cols_to_drop)

after_cols = len(listing.columns)
print(f"Columns before drop: {before_cols}, Columns after drop: {after_cols}")




numeric_cols = [
    "ClosePrice",
    "LivingArea",
    "DaysOnMarket",
    "Bedrooms",
    "Bathrooms"
]

for col in numeric_cols:

    if col in listing.columns:

        listing[col] = pd.to_numeric(listing[col], errors='coerce')

# Filter out rows with invalid numeric values
before_rows = len(listing)
listing = listing[
    (listing["ClosePrice"] > 0) &
    (listing["LivingArea"] > 0) &
    (listing["DaysOnMarket"] >= 0) &
    (listing["BedroomsTotal"] >= 0) &
    (listing["BathroomsTotalInteger"] >= 0)

]
after_rows = len(listing)
print(f"Rows before filtering: {before_rows}, Rows after filtering: {after_rows}")


# Data Consistency Checks
# 1. Listing after Close
listing["listing_after_close_flag"] = (
    listing["ListingContractDate"] > listing["CloseDate"]
)

# 2. Purchase after Close
listing["purchase_after_close_flag"] = (
    listing["PurchaseContractDate"] > listing["CloseDate"]
)

# 3. Negative timeline
listing["negative_timeline_flag"] = (
    (listing["ListingContractDate"] > listing["PurchaseContractDate"]) |
    (listing["PurchaseContractDate"] > listing["CloseDate"])
)

print("Listing after close:", listing["listing_after_close_flag"].sum())
print("Purchase after close:", listing["purchase_after_close_flag"].sum())
print("Negative timeline:", listing["negative_timeline_flag"].sum())

print(f"Total rows: {len(listing)}")
print(f"Total columns: {len(listing.columns)}")

# Flag missing coordinates
listing["missing_coordinates_flag"] = (
    listing["Latitude"].isna() | listing["Longitude"].isna()
)

# Flag zero coordinates
listing["zero_coordinates_flag"] = (
    (listing["Latitude"] == 0) | (listing["Longitude"] == 0)
)

# Flag positive longitude (invalid for California)
listing["positive_longitude_flag"] = (
    listing["Longitude"] > 0
)

# Flag out-of-bounds coordinates (California roughly between lat 32-42 and long -125 to -114)
listing["out_of_bounds_flag"] = (
    (listing["Latitude"] < 32) | (listing["Latitude"] > 42) |
    (listing["Longitude"] < -125) | (listing["Longitude"] > -114)
)

print("Missing coordinates:", listing["missing_coordinates_flag"].sum())
print("Zero coordinates:", listing["zero_coordinates_flag"].sum())
print("Positive longitude:", listing["positive_longitude_flag"].sum())
print("Out-of-bounds coordinates:", listing["out_of_bounds_flag"].sum())

listing.to_csv("/Users/li/Desktop/idx Exchange/filtered/listing_final.csv", index=False)

# Week 6
listing['PriceRatio'] = np.where(
    listing['OriginalListPrice'] > 0,
    listing['ClosePrice'] / listing['OriginalListPrice'],
    np.nan
)

listing['PricePerSqFt'] = np.where(
    listing['LivingArea'] > 0,
    listing['ClosePrice'] / listing['LivingArea'],
    np.nan
)

listing['DaysOnMarket_Clean'] = pd.to_numeric(
    listing['DaysOnMarket'],
    errors='coerce'
)

listing['Year'] = listing['CloseDate'].dt.year
listing['Month'] = listing['CloseDate'].dt.month
listing['MonthName'] = listing['CloseDate'].dt.strftime('%b')
listing['Quarter'] = listing['CloseDate'].dt.quarter

listing['YrMo'] = listing['CloseDate'].dt.strftime('%Y-%m')
listing['YearMonth'] = listing['CloseDate'].dt.to_period('M')

listing['CloseToOriginalListRatio'] = listing['PriceRatio']

listing['ListingToContractDays'] = (
    listing['PurchaseContractDate'] - listing['ListingContractDate']
).dt.days

listing['ContractToCloseDays'] = (
    listing['CloseDate'] - listing['PurchaseContractDate']
).dt.days

# Segment Analysis
# ============================================================

# 1. Property Type Analysis

# ============================================================

property_type_summary = create_segment_summary(listing, 'PropertyType')

property_subtype_summary = create_segment_summary(listing, 'PropertySubType')

# ============================================================

# 2. Geographic Analysis

# ============================================================

county_summary = create_segment_summary(listing, 'CountyOrParish')

mls_area_summary = create_segment_summary(listing, 'MLSAreaMajor')

# Optional combined geographic analysis
county_mls_summary = create_segment_summary(
    listing,
    ['CountyOrParish', 'MLSAreaMajor']
)

# ============================================================

# 3. Competitive Intelligence (Brokerage Analysis)

# ============================================================

list_office_summary = create_segment_summary(
    listing,
    'ListOfficeName',
    top_n=20          # Top 20 listing offices by volume
)

buyer_office_summary = create_segment_summary(
    listing,
    'BuyerOfficeName',
    top_n=20          # Top 20 buyer offices by volume

)

# Optional listing vs buyer office cross-analysis
office_pair_summary = create_segment_summary(
    listing,
    ['ListOfficeName', 'BuyerOfficeName'],
    top_n=50
)

# ============================================================

# 4. Export Results for Tableau

# ============================================================

segment_summaries = {
    'property_type_summary': property_type_summary,
    'property_subtype_summary': property_subtype_summary,
    'county_summary': county_summary,
    'mls_area_summary': mls_area_summary,
    'county_mls_summary': county_mls_summary,
    'list_office_summary': list_office_summary,
    'buyer_office_summary': buyer_office_summary,
    'office_pair_summary': office_pair_summary
}

for name, summary_df in segment_summaries.items():
    summary_df.to_csv(f'/Users/li/Desktop/idx Exchange/outputtable/{name}_list.csv', index=False)
    print(f"Saved {name}_list.csv ({summary_df.shape[0]} rows)")

# ============================================================

# 5. Preview Key Outputs

# ============================================================

print("\n=== Property Type Summary ===")

print(property_type_summary.head())

print("\n=== County Summary ===")

print(county_summary.head())

print("\n=== Top Listing Offices ===")

print(list_office_summary.head())

print("\n=== Top Buyer Offices ===")

print(buyer_office_summary.head())
