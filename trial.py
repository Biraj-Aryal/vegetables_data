import pandas as pd
import os

# Directory containing the CSV files
csv_directory = 'daily_prices'  # Update this with your directory path

# Get a list of CSV files in the directory
csv_files = [file for file in os.listdir(csv_directory) if file.endswith('.csv')]

# Create an empty dictionary to store the dataframes
dataframes = {}

# Iterate through the CSV files and read them into dataframes
for csv_file in csv_files:
    # Extract the date from the file name
    date = os.path.splitext(csv_file)[0]
    # Read the CSV file into a dataframe
    df = pd.read_csv(os.path.join(csv_directory, csv_file))
    # Add the dataframe to the dictionary with the date as the key
    dataframes[date] = df

# Create a merged dataframe with a multi-level index (date, vegetable)
merged_df = pd.concat(dataframes, axis=1)

# Iterate through the common indices and create new dataframes
common_indices = merged_df.index.get_level_values(1).unique()
new_dataframes = {}

for index in common_indices:
    new_df = merged_df.loc[pd.IndexSlice[:, index], ['Min Price', 'Max Price', 'Avg Price']]
    new_dataframes[f'allTime {index}'] = new_df

# Print the new dataframes
for name, df in new_dataframes.items():
    print(name)
    print(df)
    print()
