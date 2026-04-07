import pandas as pd
import glob

# Step 1: Get a list of all MLS sold CSV files in the folder
file_list = glob.glob('raw/CRMLSListing2024*.csv')  # all 2024 monthly files

# Step 2: Read each CSV into a DataFrame and store in a list
dfs = [pd.read_csv(file) for file in file_list]

# Step 3: Concatenate all DataFrames into one
sold = pd.concat(dfs, ignore_index=True)

# Step 4: Optional filtering and cleaning
sold = sold[sold['PropertyType'] == 'Residential']
# sold = sold.dropna()  # if you want to drop rows with missing values

# Step 5: Save combined dataset
sold.to_csv('filtered/CRMLSListing_Residential_2024.csv', index=False)

print("Combined CSV saved. Number of rows:", len(sold))