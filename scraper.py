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

        current_time = datetime.now().time()
        if current_time < datetime.strptime('8:00:00', '%H:%M:%S').time() or current_time >= datetime.strptime('22:00:00', '%H:%M:%S').time():
            url = f'https://www.google.nl/maps/dir/{ORIGIN}/{DESTINATION}'
        else:
            url = f'https://www.google.nl/maps/dir/{DESTINATION}/{ORIGIN}'

        print(url)
        driver.get(url)

        # save page as html
        # with open('page_source.html', 'w', encoding='utf-8') as f:
        #     f.write(driver.page_source)

        try:
            try:
                # cookies
                WebDriverWait(driver, 2).until(
                    # EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Alles afwijzen"]'))
                    EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Alle ablehnen"]')) # change to own/server lan
                ).click()
            except:
                print('No cookies')

            try:
                travel_time_element = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "Fk3sm fontHeadlineSmall delay-light")]'))
                )
                travel_time = travel_time_element.text
            except:
                print('Error while fetching travel time')

            try:
                distance_element = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "ivN21e tUEI8e fontBodyMedium")]/div'))
                )
                distance = distance_element.text
            except:
                print('Error while fetching distance')

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

    print('-------------------------------------------')

if __name__ == '__main__':
    cache_travel_info()