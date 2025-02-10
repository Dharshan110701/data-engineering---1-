import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_driver_with_random_user_agent(headless=True):
    # Set up Chrome options
    options = Options()
    if headless:
        options.add_argument("--headless")  # Ensure GUI is off
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Initialize the Chrome driver with the options
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def split_host_city_year(df):
    # Split the 'Host City' column into 'Host City' and 'Year'
    df[['Host City', 'Year']] = df['Host City'].str.extract(r'(.*)\s+(\d{4})')
   
    # Reorder columns
    df = df[['Olympiad', 'Year', 'Host City', 'Nations', 'Athletes']]
   
    return df

def scrape_olympic_data(url):
    logging.info(f"Scraping data from {url}")
   
    driver = create_driver_with_random_user_agent()
    driver.get(url)

    try:
        # Wait until all frame_space table elements are present
        tables = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'frame_space'))
        )

        # Assuming the second table is the one we want (index 1)
        table_body = tables[1]  # Change the index if it's not the second table

        # Extract the table rows
        rows = table_body.find_elements(By.TAG_NAME, 'tr')

        # Extract data from each row
        data = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            row_data = [cell.text.strip() for cell in cells]
            if row_data:  # Ensure row has data (skip empty rows if any)
                data.append(row_data)
                logging.info(f"Row data: {row_data}")

        # If data is extracted, create DataFrame
        if data:
            df = pd.DataFrame(data, columns=['Olympiad', 'Host City', 'Nations', 'Athletes'])
            logging.info(f"DataFrame: \n{df}")

            # Split host city and year
            df = split_host_city_year(df)
            logging.info(f"DataFrame after splitting host city and year: \n{df}")

            # Clean the DataFrame
            df_cleaned = clean_dataframe(df)

            # Create directory to save CSV files
            os.makedirs('csvFiles', exist_ok=True)

            # Drop the first column (index 0) from the DataFrame
            df_cleaned = df_cleaned.drop(df_cleaned.columns[0], axis=1)

            # Save to CSV
            csv_filename = os.path.join('csvFiles', 'Olympiad.csv')
            df_cleaned.to_csv(csv_filename, index=False)
            logging.info(f"Cleaned data saved to {csv_filename}")
        else:
            logging.warning("No data found in the table body.")

    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")

    finally:
        driver.quit()

def scrape_medals_by_continent(url, year):
    logging.info(f"Scraping medals data from {url} for year {year}")
   
    driver = create_driver_with_random_user_agent()
    driver.get(url)

    try:
        # Wait until all frame_space table elements are present
        tables = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'frame_space'))
        )

        # Assuming the second table is the one we want (index 2)
        table_body = tables[2]  # Change the index if it's not the second table

        # Extract the table rows
        rows = table_body.find_elements(By.TAG_NAME, 'tr')

        # Extract data from each row
        data = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            row_data = [cell.text.strip() for cell in cells]
            if row_data:  # Ensure row has data (skip empty rows if any)
                # Insert the year as the first column
                row_data.insert(0, year)
                data.append(row_data)
                logging.info(f"Row data for year {year}: {row_data}")

        # If data is extracted, create DataFrame
        if data:
            df = pd.DataFrame(data, columns=['Year', 'Rank', 'Continent', 'Flag', 'Gold', 'Silver', 'Bronze', 'Total'])
            logging.info(f"DataFrame for year {year}: \n{df}")

            return df
        else:
            logging.warning("No data found in the table body.")
            return pd.DataFrame()

    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return pd.DataFrame()

    finally:
        driver.quit()

def clean_dataframe(df):
    # Log before cleaning
    logging.info(f"Cleaning DataFrame: \n{df}")

    # Replace None, empty strings, and whitespace-only strings with NaN
    df = df.replace(r'^\s*$', pd.NA, regex=True)

    # Additional replacements for specific patterns in the medals data
    df = df.replace(to_replace=[None, 'None', 'none', 'NaN', 'nan'], value=pd.NA)

    # Remove rows where all elements are NaN
    df_cleaned = df.dropna(how='all')

    # Remove duplicates
    df_cleaned = df_cleaned.drop_duplicates()

    # Log after cleaning
    logging.info(f"Cleaned DataFrame: \n{df_cleaned}")

    return df_cleaned

# URLs to scrape for medals by continent
urls_by_year = {
    '2020': 'https://www.olympiandatabase.com/index.php?id=44917&L=1',
    '2016': 'https://www.olympiandatabase.com/index.php?id=22912&L=1',
    '2012': 'https://www.olympiandatabase.com/index.php?id=17553&L=1',
    '2008': 'https://www.olympiandatabase.com/index.php?id=15537&L=1',
    '2004': 'https://www.olympiandatabase.com/index.php?id=15547&L=1',
}

# Execute scraping function for olympiad data
url_olympiad = 'https://www.olympiandatabase.com/index.php?id=418&L=1'
scrape_olympic_data(url_olympiad)

# Execute scraping functions for medals by continent and combine the data
all_medals_data = pd.DataFrame()
for year, url in urls_by_year.items():
    medals_df = scrape_medals_by_continent(url, year)
    if not medals_df.empty:
        all_medals_data = pd.concat([all_medals_data, medals_df], ignore_index=True)

# Clean the combined medals data
cleaned_medals_data = clean_dataframe(all_medals_data)

# Create directory to save CSV files
os.makedirs('csvFiles', exist_ok=True)

# Save to CSV
csv_filename_medals = os.path.join('csvFiles', 'ContinentalMedals.csv')
cleaned_medals_data.to_csv(csv_filename_medals, index=False)
logging.info(f"Cleaned medals data saved to {csv_filename_medals}")
