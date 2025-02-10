import os
from hdfs import InsecureClient
import logging

# Configure logging
logging.basicConfig(
    filename='upload_to_hdfs.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s:%(message)s'
)

# Set up HDFS client
logging.info('Setting up HDFS client.')
hdfs_client = InsecureClient(url='http://100.118.221.23:9870', user='hadoop')

# Path to the folder containing CSV files on your local machine
local_csv_folder = 'D:/Study Material/Data_Engineering/Final_Project/Olympics_Data/code/csvFiles'
# Path in HDFS where you want to store the files
hdfs_target_folder = '/home/hadoop/data/nameNode/data/'

# Ensure the HDFS target folder exists
try:
    hdfs_client.makedirs(hdfs_target_folder)
    logging.info(f'Ensured HDFS target folder exists: {hdfs_target_folder}')
except Exception as e:
    logging.error(f'Failed to ensure HDFS target folder exists: {e}')
    raise

# Upload each CSV file to HDFS
for csv_file in os.listdir(local_csv_folder):
    if csv_file.endswith('.csv'):
        local_file_path = os.path.join(local_csv_folder, csv_file)
        hdfs_file_path = os.path.join(hdfs_target_folder, csv_file)
        try:
            hdfs_client.upload(hdfs_file_path, local_file_path)
            logging.info(f'Successfully uploaded {csv_file} to {hdfs_file_path}')
        except Exception as e:
            logging.error(f'Failed to upload {csv_file}: {e}')
