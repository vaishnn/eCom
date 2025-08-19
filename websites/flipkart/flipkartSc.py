from time import sleep
from random import uniform
import logging
from typing import Optional
from collections import defaultdict
from selenium.webdriver.common.by import By
import sys
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import re
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

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
            if self.logger:
                self.logger.info(f"Successfully searched for {product_name}")
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error searching product: {e}")
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

            if self.logger:
                self.logger.info(f"Scraped {len(products)} product details.")
            return products
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error scraping product details: {e}")
            return []

    @staticmethod
    def clean_product_data(products: list, logger=None):
        if logger:
            logger.info(f"Cleaning {len(products)} products.")
        processed_products = defaultdict(lambda: {'price': float('inf')})

        for product in products:
            title = product['title']
            price_str = product['price']
            match = re.match(r'(.*?)\s\(([^,]+),\s([^)]+)\)', title)
            if not match:
                if logger:
                    logger.debug(f"Skipping product due to no regex match: {title}")
                continue

            model, _, storage = match.groups()
            model = model.strip()
            storage = storage.strip()

            try:
                price = int(re.sub(r'[₹,]', '', price_str))
            except (ValueError, TypeError):
                if logger:
                    logger.debug(f"Skipping product due to price conversion error: {price_str}")
                continue
            product_key = (model, storage)
            # print(product_key)?
            if product_key in processed_products:
                if price < processed_products[product_key]['price']:
                    processed_products[product_key]['price'] = price
            else:
                processed_products[product_key] = {}
                processed_products[product_key]['price'] = price
        # print(processed_products)
        processed_products = [{'title': element[0] + " " + element[1], 'price': processed_products[element]['price']} for element in processed_products]

        if logger:
            logger.info(f"Returned {len(processed_products)} products after cleaning.")
        return processed_products

    def quit(self):
        if self.logger:
            self.logger.info("Quitting driver.")
        self.driver.quit()

class FlipkartLocalScraper(FlipkartScraper):
    def __init__(self, website: str, logger: Optional[logging.Logger] = None):
        super().__init__(website, logger)

    def get_driver(self):
        if self.logger:
            self.logger.info("Initializing local Chrome driver.")
        options = webdriver.ChromeOptions()
        options.add_argument("--incognito")
        # options.add_argument("--headless")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        self.driver = webdriver.Chrome(options=options)

class FlipkartServerScraper(FlipkartScraper):
    def __init__(self, website: str, logger: Optional[logging.Logger] = None):
        super().__init__(website, logger)

    def get_driver(self):
        if self.logger:
            self.logger.info("Initializing server Chrome driver.")
        options = webdriver.ChromeOptions()
        options.add_argument("--incognito")
        service = Service('/usr/bin/chromedriver') # type: ignore
        options.add_argument("--user-data-dir=/tmp/chrome-user-data")
        options.add_argument("--headless") # Runs Chrome in headless mode.
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=options, service = service)

def run(target_machine, _, product_name, logger, website: str = "https://www.flipkart.com/"):
    if target_machine == 'local':
        flipkartSc = FlipkartLocalScraper(website, logger)
    else:
        flipkartSc = FlipkartServerScraper(website, logger)
    flipkartSc.get_driver()

    search_success = flipkartSc.search_product(product_name)
    if search_success:
        products = flipkartSc.scrape_product_details()
    else:
        products = []
    flipkartSc.quit()
    if products:
        cleaned_products = flipkartSc.clean_product_data(products, logger)
        return cleaned_products
    if logger:
        logger.warning("No products found, returning empty list.")
    return []

if __name__ == "__main__":
    run_mode = "local"
    if len(sys.argv) > 1 and "--local" == sys.argv[1] or "--server" == sys.argv[1]:
        run_mode = sys.argv[1].replace("--", "")
    run(run_mode, '226030', 'Iphone 16 128gb', None)
