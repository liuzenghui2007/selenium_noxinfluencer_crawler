from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
import json

# 设置请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
}

# Initialize Selenium WebDriver with options
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# List to store the extracted data
data = []

try:
    # Navigate to the page
    base_url = "https://cn.noxinfluencer.com/youtube-channel-rank/top-100-us-all-youtuber-sorted-by-subs-weekly"
    driver.get(base_url)

    # Wait for the table body to be present
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, 'table-body'))
    )

    # Scroll to the bottom of the page to load all content
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for new content to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Get page source and parse with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    table_body = soup.find('div', id='table-body')

    # Check if table body is found
    if table_body:
        # Extract data from each row
        for row in table_body.find_all('div', class_='table-line clearfix'):
            rank_number = row.find('span', class_='rank-number').get_text(strip=True)
            description = row.find('span', class_='rank-desc').get_text(strip=True)
            category = row.find('span', class_='rank-category').get_text(strip=True)
            subscribers = row.find('span', class_='rank-subs').get_text(strip=True)
            avg_views = row.find('span', class_='rank-avg-view').get_text(strip=True)
            score = row.find('span', class_='rank-score').get_text(strip=True)

            # Append the data to the list
            data.append({
                "Rank": rank_number,
                "Description": description,
                "Category": category,
                "Subscribers": subscribers,
                "Avg Views": avg_views,
                "Score": score
            })
    else:
        print("Table not found. Please check the class name or ensure the page is fully loaded.")

finally:
    # Close the WebDriver
    driver.quit()

# Convert the list of data to a DataFrame
df = pd.DataFrame(data)

# Save the DataFrame to a CSV file
df.to_csv('youtube_data.csv', index=False, encoding='utf-8-sig')

