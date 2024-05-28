# scraper.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json
import time
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv(".env")

ORIGIN = os.getenv('ORIGIN')
DESTINATION = os.getenv('DESTINATION')
CACHE_FILE = os.getenv('CACHE_FILE')

def fetch_travel_time():
    service = Service(ChromeDriverManager().install())
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    if os.getenv('ENV') == 'production':
        service = Service(executable_path=r'/usr/local/bin/chromedriver')
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
        options.add_argument("--window-size=1920,1080")

    with webdriver.Chrome(service=service, options=options) as driver:
        url = f'https://www.google.com/maps/dir/{ORIGIN}/{DESTINATION}'
        driver.get(url)

        try:
            # cookies
            WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Alles afwijzen"]')) # change to own lan
            ).click()

            travel_time_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "Fk3sm fontHeadlineSmall delay-light")]'))
            )
            travel_time = travel_time_element.text

            distance_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "ivN21e tUEI8e fontBodyMedium")]/div'))
            )
            distance = distance_element.text

            return travel_time, distance
        except Exception as e:
            print(f'Error fetching travel info: {e}')
            return None, None

def cache_travel_info():
    travel_time, distance = fetch_travel_time()
    if travel_time and distance:
        current_time = datetime.now().strftime('%d-%m-%Y %H:%M:%S') # or unix
        with open(CACHE_FILE, 'w') as f:
            json.dump({'travel_time': travel_time, 'distance': distance, 'timestamp': current_time}, f)
        print(f'Cached travel time: {travel_time}, distance: {distance}, timestamp: {current_time}')
    else:
        print('Failed to fetch travel info')

if __name__ == '__main__':
    cache_travel_info()