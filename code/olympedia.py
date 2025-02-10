import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import logging

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

def clean_dataframe(df):
    # Log before cleaning
    logging.info(f"Cleaning DataFrame: \n{df}")

    # Replace None, empty strings, and whitespace-only strings with NaN
    df = df.replace(r'^\s*$', pd.NA, regex=True)

    # Additional replacements for specific patterns in the data
    df = df.replace(to_replace=[None, 'None', 'none', 'NaN', 'nan'], value=pd.NA)

    # Remove rows where all elements are NaN
    df_cleaned = df.dropna(how='all')

    # Remove duplicates
    df_cleaned = df_cleaned.drop_duplicates()

    # Log after cleaning
    logging.info(f"Cleaned DataFrame: \n{df_cleaned}")

    return df_cleaned

def scrape_olympic_sports(url):
    logging.info(f"Scraping data from {url}")
    
    driver = create_driver_with_random_user_agent()
    driver.get(url)

    try:
        # Wait until the table is present
        table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'table-striped'))
        )

        # Extract table head
        table_head = table.find_element(By.TAG_NAME, 'thead')
        headers = [header.text.strip() for header in table_head.find_elements(By.TAG_NAME, 'th')]
        logging.info(f"Table headers: {headers}")

        # Extract table body
        table_body = table.find_element(By.TAG_NAME, 'tbody')
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
            df = pd.DataFrame(data, columns=headers)
            logging.info(f"DataFrame: \n{df}")

            # Clean the DataFrame
            df_cleaned = clean_dataframe(df)

            # Ensure the csvFiles directory exists
            if not os.path.exists('csvFiles'):
                os.makedirs('csvFiles')

            # Save to CSV within the csvFiles directory
            csv_filename = os.path.join('csvFiles', 'Sports.csv')
            df_cleaned.to_csv(csv_filename, index=False)
            logging.info(f"Cleaned data saved to {csv_filename}")
        else:
            logging.warning("No data found in the table body.")

    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")

    finally:
        driver.quit()

# URL to scrape
url_sports = 'https://www.olympedia.org/sports'
scrape_olympic_sports(url_sports)
