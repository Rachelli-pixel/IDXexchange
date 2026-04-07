import pandas as pd
sold1 = pd.read_csv('raw/CRMLSSold202401.csv')
sold2 = pd.read_csv('raw/CRMLSSold202402.csv')
sold = pd.concat([sold1, sold2])

sold.columns
sold.head()

sold['PropertyType'].unique()
sold = sold[sold.PropertyType == 'Residential']
sold.isnull().sum()

sold.to_csv('filtered/CRMLSSold_Residential.csv', index=False)