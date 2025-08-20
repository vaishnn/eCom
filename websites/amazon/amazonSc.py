from time import sleep
from random import uniform
import logging
from typing import Optional
import sys
import re
from collections import defaultdict
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

class AmazonScraper:
    def __init__(self, website: str , logger: Optional[logging.Logger] = None):
        self.website = website
        self.driver: webdriver.Chrome | webdriver.Firefox
        self.logger = logger

    def change_location(self, zip_code: str) -> bool:
        try:
            self.driver.get(self.website)
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
            if self.logger:
                self.logger.info(f"Location changed to {zip_code}")
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"Could not change location to {zip_code}. Error: {e}")
            self.driver.quit()
            return False

    def search_product(self, product_name: str) -> bool:
        try:
            search_bar = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))
            )
            # search_bar.clear()
            search_bar.send_keys(product_name)
            sleep(uniform(1,3))
            search_bar.send_keys(Keys.RETURN)

            if self.logger:
                self.logger.info(f"Product search initiated for {product_name}")
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"Could not search for {product_name}. Error: {e}")
            self.driver.quit()
            return False
    def scrape_product_details(self) -> list:
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        products = []

        results = soup.find_all("div", {"data-component-type": "s-search-result"})
        for item in results:
            if item.find("span", string=lambda text: text and "Sponsored" in text): #type: ignore
                if self.logger:
                    self.logger.debug("Skipping sponsored product.")
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
        if self.logger:
            self.logger.info(f"Scraped {len(products)} product details.")
        return products

    @staticmethod
    def clean_product_data(products, needed_product, logger=None):
        if logger:
            logger.info(f"Cleaning {len(products)} products.")
        processed_products = defaultdict(lambda: {'price': float('inf')})
        for item in products:
            title = item.get('title', '')
            price_str = item.get('price', '0')
            match = re.match(r'^(.*?)\s(?:(\d+\sGB)|(?:\((\d+\sGB)\)))', title)

            if not match:
                continue
            model = match.group(1).strip()
            storage = next((s for s in match.groups()[1:] if s is not None), None)

            if not storage:
                continue

            product_key = (model, storage)
            try:
                price = int(price_str)
            except (ValueError, TypeError):
                continue

            if price == 0:
                continue
            if price < processed_products[product_key]['price']:
                processed_products[product_key]['price'] = price
                processed_products[product_key]['title'] = f"{model} {storage}" # type: ignore

        cleaned_products = list(processed_products.values())
        if logger:
            logger.info(f"Returned {len(cleaned_products)} products after cleaning.")
        return cleaned_products


    def quit(self):
        if self.logger:
            self.logger.info("Quitting driver.")
        self.driver.quit()


class AmazonLocalScraper(AmazonScraper):
    def __init__(self, website: str, logger: Optional[logging.Logger] = None):
        super().__init__(website=website, logger=logger)

    def get_driver(self):
        if self.logger:
            self.logger.info("Initializing local Chrome driver.")
        options = webdriver.ChromeOptions()

        options.add_argument("--incognito")
        # options.add_argument("--headless")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        self.driver = webdriver.Chrome(options=options)

class AmazonServerScraper(AmazonScraper):
    def __init__(self, website: str, logger: Optional[logging.Logger] = None):
        super().__init__(website=website, logger=logger)

    def get_driver(self):
        if self.logger:
            self.logger.info("Initializing server Chrome driver.")
        options = webdriver.ChromeOptions()
        options.add_argument("--incognito")
        service = Service('/usr/bin/chromedriver') # type: ignore
        options.add_argument("--user-data-dir=/tmp/chrome-user-data")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=options, service = service)

def run(target_machine, pincode, product_name, logger, website: str = "https://www.amazon.in"):
    if target_machine == 'local':
        amazonSc = AmazonLocalScraper(website, logger)
    else:
        amazonSc = AmazonServerScraper(website, logger)
    amazonSc.get_driver()
    location_success = amazonSc.change_location(pincode)
    if location_success:
        search_success = amazonSc.search_product(product_name)
        if search_success:
            products = amazonSc.scrape_product_details()
        else:
            products = []
    else:
        products = []
    amazonSc.quit()
    if products:
        cleaned_products = amazonSc.clean_product_data(products, product_name, logger)
        return cleaned_products
    if logger:
        logger.warning("No products found, returning empty list.")
    return []

if __name__ == "__main__":
    run_mode = "local"
    if len(sys.argv) > 1:
        if "--local" == sys.argv[1] or "--server" == sys.argv[1]:
            run_mode = sys.argv[1].replace("--", "")
    products = run(run_mode, '226030', 'iPhone 16 128 GB', None)
    print(products)
