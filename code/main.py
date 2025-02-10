import subprocess
import threading
import logging
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

final_status = []
# Function to run a scraping script
def run_scraping_script(script_name):
    logging.info(f"Starting scraping with {script_name}")
    subprocess.run(["python", script_name])
    logging.info(f"Finished scraping with {script_name}")
    final_status.append(script_name)

def main():
    # Define the scraping scripts
    scripts = ["espn.py", "olympedia.py", "olympianDatabase.py"]
    # scripts = ["espn.py"]
    
    # Start threading for each scraping script
    threads = []
    for script in scripts:
        thread = threading.Thread(target=run_scraping_script, args=(script,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    logging.info(final_status)

if __name__ == "__main__":
    main()
