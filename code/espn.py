import os
import time
import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import logging
from fake_useragent import UserAgent
from sqlalchemy import create_engine

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_driver_with_random_user_agent(headless=True):
    # Generate a random User-Agent
    user_agent = UserAgent().random

    # Set up Chrome options
    options = Options()
    if headless:
        options.add_argument("--headless")  # Ensure GUI is off
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f'user-agent={user_agent}')

    # Initialize the Chrome driver with the options
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def download_image(url, save_path):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        with open(save_path, 'wb') as f:
            f.write(response.content)
        logging.info(f"Downloaded image to {save_path}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to download image from {url}: {str(e)}")

def scrape_table_data(url, year, data_type):
    logging.info(f"Scraping {data_type} data for {year} from {url}")
    
    driver = create_driver_with_random_user_agent(False)
    driver.get(url)

    # Wait until the table is present
    table = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'table.medals.olympics.has-team-logos'))
    )

    # Extract the table headers
    headers = [th.text for th in table.find_elements(By.CSS_SELECTOR, 'thead th')]
    logging.info(f"Table headers: {headers}")

    # Add header for the flag URL
    headers.append('Flag URL')

    # Extract the table rows
    rows = table.find_elements(By.CSS_SELECTOR, 'tbody tr')

    # Create directory to save flag images
    os.makedirs('flag_images', exist_ok=True)

    # Extract data from each row
    data = []
    for row in rows:
        cols = row.find_elements(By.CSS_SELECTOR, 'td')
        cols_text = [col.text for col in cols]

        # Try to get the flag URL
        flag_url = ""
        try:
            flag_url = row.find_element(By.CSS_SELECTOR, 'td.team img').get_attribute('src')
            flag_filename = flag_url.split('/')[-1].split('&')[0]  # Extract filename from URL
            flag_save_path = os.path.join('flag_images', flag_filename)
            download_image(flag_url, flag_save_path)
        except Exception as e:
            flag_url = None
            flag_save_path = None
            logging.warning(f"No flag image found for row: {cols_text}, setting Flag URL to None.")

        # Add year and flag URL to the row data
        row_data = dict(zip(headers, cols_text))
        row_data['Year'] = year
        row_data['Flag URL'] = flag_url
        data.append(row_data)
        logging.info(f"Row data for {year}: {cols_text} with Flag URL: {flag_url}")

    driver.quit()
    return data

def scrape_athlete_data(url, year):
    logging.info(f"Scraping athlete data for {year} from {url}")
    all_data = []

    for page in range(1, 2):  # Iterate over the first 2 pages
        paginated_url = f"{url}/sort/total/page/{page}"
        logging.info(f"Opening URL: {paginated_url}")

        driver = create_driver_with_random_user_agent()
        driver.get(paginated_url)

        # Wait until the table is present
        table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'table.medals.olympics.has-team-logos'))
        )

        # Extract the table headers
        headers = [th.text for th in table.find_elements(By.CSS_SELECTOR, 'thead th')]
        logging.info(f"Table headers: {headers}")

        # Extract the table rows
        rows = table.find_elements(By.CSS_SELECTOR, 'tbody tr')

        # Extract data from each row
        for row in rows:
            cols = row.find_elements(By.CSS_SELECTOR, 'td')
            cols = [col.text for col in cols]
            # Add year to the row data
            row_data = dict(zip(headers, cols))
            row_data['Year'] = year
            all_data.append(row_data)
            logging.info(f"Row data for {year}, page {page}: {cols}")

        driver.quit()
    return all_data

def clean_data(df):
    # Check for null values
    if df.isnull().sum().sum() > 0:
        logging.info("Null values found in the DataFrame, filling them with 'Unknown'.")
        df = df.fillna('Unknown')

    # Check for duplicates
    if df.duplicated().sum() > 0:
        logging.info("Duplicates found in the DataFrame, removing them.")
        df = df.drop_duplicates()

    return df

def main():
    # Ensure the csvFiles directory exists
    os.makedirs('csvFiles', exist_ok=True)

    # URLs to scrape for country medals
    country_url_list = {
        2004: 'https://www.espn.com/olympics/summer/2004/medals/_/view/overall',
        2008: 'https://www.espn.com/olympics/summer/2008/medals/_/view/overall',
        2012: 'https://www.espn.com/olympics/summer/2012/medals/_/view/overall',
        2016: 'https://www.espn.com/olympics/summer/2016/medals/_/view/overall',
        2020: 'https://www.espn.com/olympics/summer/2020/medals/_/view/overall'
    }

    # URLs to scrape for athletes
    athletes_url_list = {
        2004: 'https://www.espn.com/olympics/summer/2004/medals/_/view/athletes',
        2008: 'https://www.espn.com/olympics/summer/2008/medals/_/view/athletes',
        2012: 'https://www.espn.com/olympics/summer/2012/medals/_/view/athletes',
        2016: 'https://www.espn.com/olympics/summer/2016/medals/_/view/athletes',
        2020: 'https://www.espn.com/olympics/summer/2020/medals/_/view/athletes'
    }

    # List to hold all country medals data
    all_country_data = []

    # List to hold all athletes data
    all_athlete_data = []

    # Scrape country medals data
    try:
        for year, url in country_url_list.items():
            country_data = scrape_table_data(url, year, 'country medals')
            all_country_data.extend(country_data)

    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")

    # Scrape athletes data
    try:
        for year, url in athletes_url_list.items():
            athlete_data = scrape_athlete_data(url, year)
            all_athlete_data.extend(athlete_data)

    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")

    # Create pandas DataFrames
    df_country = pd.DataFrame(all_country_data)
    df_athlete = pd.DataFrame(all_athlete_data)

    # Clean DataFrames
    df_country = clean_data(df_country)
    df_athlete = clean_data(df_athlete)

    # Print the DataFrames
    print(df_country)
    print(df_athlete)

    # Save DataFrames to CSV within csvFiles directory
    df_country.to_csv(os.path.join('csvFiles', 'CountryMedals.csv'), index=False)
    df_athlete.to_csv(os.path.join('csvFiles', 'AthletesMedals.csv'), index=False)

if __name__ == "__main__":
    main()
