import pandas as pd
from hdfs import InsecureClient
from sqlalchemy import create_engine
import os
import logging

# Configure logging
logging.basicConfig(
    filename='data_import.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s:%(message)s'
)

# HDFS connection details
hdfs_host = 'http://100.118.221.23:9870'
hdfs_user = 'hadoop'
hdfs_client = InsecureClient(hdfs_host, user=hdfs_user)

# List of tables and their corresponding HDFS paths
hdfs_directory = "/home/hadoop/data/nameNode/data/"
tables = {
    'Olympiad': hdfs_directory + 'Olympiad.csv',
    'ContinentalMedals': hdfs_directory + 'ContinentalMedals.csv',
    'Sports': hdfs_directory + 'Sports.csv',
    'AthletesMedals': hdfs_directory + 'AthletesMedals.csv',
    'CountryMedals': hdfs_directory + 'CountryMedals.csv'
}

# MySQL database connection details
db_username = 'root'
db_password = '1234'
db_host = '192.168.56.101'
db_port = '3306'  # Default MySQL port
db_name = 'dataengg'

# Create a connection string
connection_string = f'mysql+pymysql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}'

# Create an SQLAlchemy engine
engine = create_engine(connection_string)

# Function to read CSV from HDFS and convert to Pandas DataFrame
def read_hdfs_csv(hdfs_path):
    try:
        with hdfs_client.read(hdfs_path, encoding='utf-8') as reader:
            logging.info(f'Reading CSV file from HDFS path: {hdfs_path}')
            return pd.read_csv(reader)
    except Exception as e:
        logging.error(f'Failed to read CSV from HDFS path {hdfs_path}: {e}')
        raise

# # Function to read Excel from HDFS and convert to Pandas DataFrame
# def read_hdfs_excel(hdfs_path):
#     try:
#         with hdfs_client.read(hdfs_path) as reader:
#             logging.info(f'Reading Excel file from HDFS path: {hdfs_path}')
#             return pd.read_excel(reader)
#     except Exception as e:
#         logging.error(f'Failed to read Excel from HDFS path {hdfs_path}: {e}')
#         raise

# Iterate over the tables dictionary
for table_name, hdfs_path in tables.items():
    try:
        logging.info(f'Processing table: {table_name} from path: {hdfs_path}')
        if hdfs_path.endswith('.csv'):
            # Read CSV file from HDFS into a Pandas DataFrame
            pandas_df = read_hdfs_csv(hdfs_path)
        # elif hdfs_path.endswith('.xls') or hdfs_path.endswith('.xlsx'):
        #     # Read Excel file from HDFS into a Pandas DataFrame
        #     pandas_df = read_hdfs_excel(hdfs_path)
        else:
            logging.warning(f'Unsupported file type: {hdfs_path}')
            continue

        # Insert data into SQL table
        pandas_df.to_sql(name=table_name, con=engine, if_exists='append', index=False)
        logging.info(f'Successfully inserted data into {table_name}')
    except Exception as e:
        logging.error(f'Failed to insert data into {table_name}: {e}')
