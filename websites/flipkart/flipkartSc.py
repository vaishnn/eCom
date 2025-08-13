from dotenv import load_dotenv
from os import getenv
from time import sleep
from random import uniform
import logging
from typing import Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
load_dotenv()
Service = None

if getenv('TARGET_MACHINE') == 'local':
    pass
if getenv('TARGET_MACHINE') == 'server':
    from selenium.webdriver.chrome.service import Service

class FlipkartScraper:
    def __init__(self, website: str, logger: Optional[logging.Logger] = None):
        self.website = website
        self.driver: webdriver.Chrome | webdriver.Firefox
        self.logger = logger

    def search_product(self, product_name: str) -> bool:
        try:
            self.driver.get(self.website)
            sleep(uniform(2, 4))
            search_bar = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="container"]/div/div[1]/div/div/div/div/div/div/div/div/div/div[1]/div/div/header/div[1]/div[2]/form/div/div/input'))
            )
            search_bar.click()
            sleep(uniform(1, 3))
            search_bar.send_keys(product_name)
            sleep(0.5)
            search_bar.send_keys(Keys.RETURN)
            sleep(uniform(2, 4))
            return True
        except Exception as e:
            print(f"Error searching product: {e}")
            return False
    def scrape_product_details(self) -> list:
        try:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            results = soup.find_all('div', class_ = '_75nlfW')

            products = []
            for result in results:
                title = result.find('div', class_ = 'KzDlHZ') #type: ignore
                rating = result.find('div', class_ = 'XQDdHH') #type: ignore
                price = result.find('div', class_ = 'Nx9bqj _4b5DiR') #type: ignore

                title = title.text.strip() if title else "N/A"
                rating = rating.text.strip() if rating else "N/A"
                price = price.text.strip() if price else "N/A"

                products.append({
                    'title': title,
                    'rating': rating,
                    'price': price
                })

            return products
        except Exception as e:
            print(f"Error scraping product details: {e}")
            return []

    def quit(self):
        self.driver.quit()

class FlipkartLocalScraper(FlipkartScraper):
    def __init__(self, website = "https://www.flipkart.com"):
        super().__init__(website=website)

    def get_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--incognito")
        # options.add_argument("--headless")?
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        self.driver = webdriver.Chrome(options=options)

class FlipkartServerScraper(FlipkartScraper):
    def __init__(self, website = "https://www.flipkart.com"):
        super().__init__(website=website)

    def get_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--incognito")
        service = Service('/usr/bin/chromedriver') # type: ignore
        options.add_argument("--user-data-dir=/tmp/chrome-user-data")
        options.add_argument("--headless") # Runs Chrome in headless mode.
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=options, service = service)

if __name__ == "__main__":
    flipSc: FlipkartServerScraper | FlipkartLocalScraper
    if getenv('TARGET_MACHINE') == 'local':
        flipSc = FlipkartLocalScraper()
    else:
        flipSc = FlipkartServerScraper()
    flipSc.get_driver()
    flipSc.search_product("Iphone 16 128gb")
    products = flipSc.scrape_product_details()
    print(products)
    flipSc.quit()
