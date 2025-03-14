import pandas as pd

# Load the workers CSV file for data cleaning
workers_file_path = 'path_to_your_workers.csv'  # Update with your correct path

# Load the data
df = pd.read_csv("workers.csv")

# Check for missing values and data types before cleaning
print("Before cleaning:")
print(df.isnull().sum())
print(df.dtypes)

# Fill missing Worker_ID and entry_ID with 0 and convert to int
df['Worker_ID'] = df['Worker_ID'].fillna(0).astype(int)
df['entry_ID'] = df['entry_ID'].fillna(0).astype(int)

# Convert date_entry to datetime, handle errors by converting invalid dates to NaT
df['date_entry'] = pd.to_datetime(df['date_entry'], errors='coerce')

# Check for missing values and data types after cleaning
print("After cleaning:")
print(df.isnull().sum())
print(df.dtypes)

# Save the cleaned data to a new CSV file
df.to_csv('cleaned_workers.csv', index=False)
