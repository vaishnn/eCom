from time import sleep
from random import uniform
from numpy import nan
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC
import sys
from selenium import webdriver
import re
from collections import defaultdict

class RelianceScraper:
    def __init__(self, logger, website: str):
        self.logger = logger
        self.driver: webdriver.Chrome | webdriver.Firefox
        self.website = website

    def change_location(self, pincode: str) -> bool:
        try:
            self.driver.get(self.website)
        except Exception:
            if self.logger:
                self.logger.error("Error occurred while navigating to Reliance Digital")
            return False
        sleep(uniform(2, 4))
        try:
            updates_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'wzrk-cancel'))
            )
            if updates_button: #type: ignore
                updates_button.click()
                sleep(uniform(2, 4))
            pick_location = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="address-pincode-button"]/span'))
            )
            pick_location.click()
            sleep(uniform(2, 4))
        except Exception:
            if self.logger:
                self.logger.error("Error occurred while finding location bar")
            return False
        try:
            pincode_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="input-pincode"]'))
            )
            pincode_input.send_keys(pincode)
            sleep(0.2)
            pincode_input.send_keys(Keys.ENTER)
            sleep(uniform(2, 4))
            if self.logger:
                self.logger.info(f"Successfully changed location to {pincode}")
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error occurred while changing location to {pincode}: {e}")
            return False


    def search_product(self, product_name: str) -> bool:
        try:
            search_bar = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div[1]/div[2]/div/div/div[1]/input'))
            )
            search_bar.click()
            sleep(uniform(1, 2))
            search_bar.send_keys(product_name)
            sleep(0.4)
            search_bar.send_keys(Keys.ENTER)
            if self.logger:
                self.logger.info(f"Successfully searched for product: {product_name}")
            return True
        except Exception:
            if self.logger:
                self.logger.error(f"Error occurred while searching for product {product_name}")
            return False

    def scrape_product_details(self) -> list:
        sleep(uniform(2, 4))
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        list_products = []
        results = soup.find_all("div", class_="product-card") # type: ignore
        for product in results:
            name = product.find("div", class_="product-card-title") #type: ignore
            price = product.find("div", class_="price") #type: ignore
            rating_re = product.find_all("svg") #type: ignore
            rating = 0
            if not rating_re:
                rating: float = nan
            else:
                for ratings in rating_re:
                    _stars = ratings.find("path", fill="#F7AB20") #type: ignore
                    if _stars:
                        rating += 1
            half_stars = product.find("img", alt="star-half") #type: ignore
            if half_stars:
                rating += 0.5

            list_products.append({
                "name": name.text.strip(), # type: ignore
                "price": price.text.strip(), # type: ignore
                "rating": rating # type: ignore
            })
        if self.logger:
            self.logger.info(f"Scraped {len(list_products)} product details")
        return list_products

    @staticmethod
    def clean_data(products: list, logger=None):
        if logger:
            logger.info(f"Cleaning {len(products)} products.")
        processed_products = defaultdict(lambda: {'price': float('inf')})
        for item in products:
            name = item.get('name', '')
            price_str = item.get('price', '₹0')
            match = re.match(r'(.*?)\s(\d+\sGB),\s(.*)', name)
            if not match:
                continue
            model, storage, _ = match.groups()
            model = model.strip()
            product_key = (model, storage)
            try:
                price = int(float(re.sub(r'[₹,]', '', price_str)))
            except (ValueError, TypeError):
                price = 0
            if price < processed_products[product_key]['price']:
                processed_products[product_key]['price'] = price
                processed_products[product_key]['title'] = f"{model}, {storage}" # type: ignore

        final_products = [data for data in processed_products.values() if 'title' in data]
        if logger:
            logger.info(f"Finished cleaning. Returning {len(final_products)} products.")
        return final_products

    def quit(self):
        if self.logger:
            self.logger.info("Quitting driver.")
        self.driver.quit()


class RelianceLocalScraper(RelianceScraper):
    def __init__(self, logger, website = "https://www.reliancedigital.in/"):
        super().__init__(logger, website)

    def get_driver(self):
        if self.logger:
            self.logger.info("Initializing local Chrome driver.")
        options = webdriver.ChromeOptions()
        options.add_argument("--incognito")
        # options.add_argument("--headless")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        self.driver = webdriver.Chrome(options=options)

class RelianceServerScraper(RelianceScraper):
    def __init__(self, logger, website = "https://www.reliancedigital.in/"):
        super().__init__(logger, website)

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

def run(target_machine, pincode, product, logger, website = "https://www.reliancedigital.in/"):
    if target_machine == 'local':
        relianceSc = RelianceLocalScraper(logger, website)
    else:
        relianceSc = RelianceServerScraper(logger, website)
    relianceSc.get_driver()
    location_success = relianceSc.change_location(pincode = pincode)
    if location_success:
        searching_success = relianceSc.search_product(product)
        if searching_success:
            products = relianceSc.scrape_product_details()
        else:
            products = []
    else:
        products = []
    # print(products)
    relianceSc.quit()
    if product != []:
        cleaned_products = RelianceScraper.clean_data(products, logger)
        return cleaned_products
    return []

if __name__ == "__main__":
    run_mode = "local"
    if len(sys.argv) > 1 and "--local" == sys.argv[1] or "--server" == sys.argv[1]:
        run_mode = sys.argv[1].replace("--", "")
    run(run_mode, '226030', 'Iphone 16 128gb', None)
