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

class AmazonScraper:
    def __init__(self, website: str = "https://www.amazon.in", logger: Optional[logging.Logger] = None):
        self.website = website
        self.driver: webdriver.Chrome | webdriver.Firefox
        self.logger = logger

    def change_location(self, zip_code: str) -> bool:
        try:
            self.driver.get("https://www.amazon.in")
            sleep(uniform(2, 4))

            location_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "glow-ingress-block"))
            )
            location_button.click()
            sleep(uniform(2, 4))

            zip_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "GLUXZipUpdateInput"))
            )
            zip_input.send_keys(str(zip_code))
            sleep(uniform(2, 4))

            apply_button = self.driver.find_element(By.ID, "GLUXZipUpdate")
            apply_button.click()
            sleep(uniform(2, 4))
            # self.logger.info("Location changed to {}".format(zip_code))
            return True
        except Exception as e:
            # self.logger.error(f"Could not change location to {zip_code}. Error: {e}")
            self.driver.quit()
            return False

    def search_product(self, product_name: str) -> bool:
        try:
            search_bar = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))
            )
            search_bar.clear()
            search_bar.send_keys(product_name)
            search_bar.send_keys(Keys.RETURN)
            sleep(uniform(2, 4))
            # logger.info("Product search initiated for {}".format(product_name))
            return True
        except Exception as e:
            # logger.error(f"Could not search for {product_name}. Error: {e}")
            self.driver.quit()
            return False
    def scrape_product_details(self) -> list:
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        products = []

        results = soup.find_all("div", {"data-component-type": "s-search-result"})
        for item in results:
            if item.find("span", string=lambda text: text and "Sponsored" in text): #type: ignore
                print("Skipping This")
                continue
            title_element = item.find("h2", class_ = "a-size-medium a-spacing-none a-color-base a-text-normal") #type: ignore
            price_amount = item.find("span", class_ = "a-price-whole") #type: ignore
            rating_element = item.find("span", class_="a-icon-alt") #type: ignore

            title_element = title_element.text.strip()if title_element else "N/A"
            price_amount = price_amount.text.strip().replace(",", "") if price_amount else "N/A"
            rating_element = rating_element.text.strip() if rating_element else "N/A"

            if title_element != "N/A":
                products.append({
                    "title": title_element,
                    "price": price_amount,
                    "rating": rating_element
                })
        return products


class AmazonLocalScraper(AmazonScraper):
    def __init__(self):
        super().__init__()

    def get_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--incognito")
        # options.add_argument("--headless")?
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        self.driver = webdriver.Chrome(options=options)

class AmazonServerScraper(AmazonScraper):
    def __init__(self):
        super().__init__()

    def get_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--incognito")
        service = Service('/usr/bin/chromedriver') # type: ignore
        options.add_argument("--user-data-dir=/tmp/chrome-user-data")
        options.add_argument("--headless") # Runs Chrome in headless mode.
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=options, service = service)
