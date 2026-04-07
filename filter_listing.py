import pandas as pd
import glob

# Step 1: Get a list of all MLS sold CSV files in the folder
file_list = glob.glob('raw/*Listing*.csv')

# Step 2: Read each CSV into a DataFrame and store in a list
dfs = [pd.read_csv(file) for file in file_list]

# Step 3: Concatenate all DataFrames into one
Listing = pd.concat(dfs, ignore_index=True)

# Step 4: Optional filtering and cleaning
Listing = Listing[Listing['PropertyType'] == 'Residential']
# Listing = Listing.dropna()

# Step 5: Save combined dataset
Listing.to_csv('filtered/CRMLSListing_Residential.csv', index=False)

print("Combined CSV saved. Number of rows:", len(Listing))