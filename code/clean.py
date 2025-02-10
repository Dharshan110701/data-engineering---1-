import pandas as pd
import os

# File paths for the CSV files
file_paths = {
    'AthletesMedals.csv': 'D:/Study Material/Data_Engineering/Final_Project/Olympics_Data/code/csvFiles/AthletesMedals.csv',
    'Olympiad.csv': 'D:/Study Material/Data_Engineering/Final_Project/Olympics_Data/code/csvFiles/Olympiad.csv',
    'ContinentalMedals.csv': 'D:/Study Material/Data_Engineering/Final_Project/Olympics_Data/code/csvFiles/ContinentalMedals.csv',
    'Sports.csv': 'D:/Study Material/Data_Engineering/Final_Project/Olympics_Data/code/csvFiles/Sports.csv',
    'CountryMedals.csv': 'D:/Study Material/Data_Engineering/Final_Project/Olympics_Data/code/csvFiles/CountryMedals.csv'
}

# Column name mappings for each file
column_mappings = {
    'AthletesMedals.csv': {
        'GROUP': 'Team',
        'G': 'Gold',
        'S': 'Silver',
        'B': 'Bronze',
        'TOTAL': 'Total',
        'Year': 'Years',
        'Flag URL': 'Flag_URL'
    },
    'Olympiad.csv': {
        'Year': 'Years'
    },
    'ContinentalMedals.csv': {
        'Year': 'Years',
        'Position': 'Position',
        'Continent': 'Continent',
        'Gold': 'Gold',
        'Silver': 'Silver',
        'Bronze': 'Bronze',
        'Total': 'Total'
    },
    'Sports.csv': {
        'Olympic Status': 'Olympic_Status'
    },
    'CountryMedals.csv': {
        'GROUP': 'Team',
        'G': 'Gold',
        'S': 'Silver',
        'B': 'Bronze',
        'TOTAL': 'Total',
        'Year': 'Years',
        'Flag URL': 'Flag_URL'
    }
}

# Process each file
for filename, file_path in file_paths.items():
    if os.path.exists(file_path):
        try:
            # Read the CSV file into a DataFrame
            df = pd.read_csv(file_path)

            # Rename columns as per the mappings for each file
            if filename in column_mappings:
                df = df.rename(columns=column_mappings[filename])

            # Save the updated DataFrame back to the CSV file
            df.to_csv(file_path, index=False)

            # Display the first few rows of the DataFrame to verify
            print(f"First few rows of {filename} after column renaming:")
            print(df.head())

        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
    else:
        print(f"File {filename} not found at {file_path}")
