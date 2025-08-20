from time import sleep
from random import uniform
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import re
import sys
from collections import defaultdict
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

class CromaScraper:
    def __init__(self, logger, website: str):
        self.logger = logger
        self.driver: webdriver.Chrome | webdriver.Firefox
        self.website = website

    def change_location(self, zip_code: str) -> bool:
        try:
            self.driver.get(self.website)
            sleep(uniform(2, 4))
            location_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="container"]/div/div[1]/div[1]/div/div[6]/div[2]/div[1]/div'))
            )
            location_button.click()
            sleep(uniform(2, 4))
            zip_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[5]/div[3]/div/div/div/div/div[1]/input'))
            )

            for _ in range(6):
                zip_input.send_keys(Keys.BACKSPACE)
                sleep(uniform(0.1, 0.3))

            zip_input.send_keys(str(zip_code))
            sleep(uniform(2, 4))
            update_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="apply-pincode-btn"]'))
            )
            update_button.click()
            sleep(uniform(2, 4))
            if self.logger:
                self.logger.info(f"Successfully changed location to {zip_code}")
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error changing location to {zip_code}: {e}")
            return False

    def search_product(self, product: str) -> bool:
        try:
            search_bar = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="searchV2"]'))
            )
            search_bar.click()
            sleep(uniform(1, 3))
            search_bar.send_keys(product)
            sleep(uniform(1, 3))
            search_bar.send_keys(Keys.RETURN)
            sleep(uniform(2, 4))
            if self.logger:
                self.logger.info(f"Successfully searched for {product}")
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error searching for {product}: {e}")
            return False

    def scrape_product_details(self) -> list:
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        product_details = []

        results = soup.find_all("div", class_="cp-product typ-plp plp-srp-typ")
        for result in results:
            # No need to skip Sponsored Stuff
            product_name = result.find("h3", class_ = "product-title plp-prod-title 999") # type: ignore
            product_price = result.find("div", class_= "new-price plp-srp-new-price-cont") # type: ignore
            product_rating = result.find("span", class_ = "rating-text") # type: ignore

            product_name = product_name.text.strip() if product_name else "N/A"
            product_price = product_price.text.strip().split(" ")[0].replace("₹", "").replace(",", "") if product_price else "N/A"
            product_rating = product_rating.text.strip() if product_rating else "N/A"

            if product_name == "N/A":
                continue

            product_details.append({
                "name": product_name,
                "price": product_price,
                "rating": product_rating
            })
        if self.logger:
            self.logger.info(f"Scraped {len(product_details)} product details")
        return product_details

    @staticmethod
    def clean_product_data(products, logger=None):
        if logger:
            logger.info(f"Cleaning {len(products)} products.")
        processed_products = defaultdict(lambda: {'price': float('inf')})

        for item in products:
            name = item.get('name', '')
            price_str = item.get('price', '0')

            match = re.match(r'(.*?)\s\((\d+GB),\s([^)]+)\)', name)
            if not match:
                continue

            model, storage, _ = match.groups()
            model = model.replace('Apple', '').strip()
            storage = storage.strip().replace('GB', ' GB')

            product_key = (model, storage)

            try:
                price = int(price_str)
            except (ValueError, TypeError):
                price = 0

            if price < processed_products[product_key]['price']:
                processed_products[product_key]['price'] = price
                processed_products[product_key]['title'] = f"{model} {storage}" # type: ignore

        cleaned_products = [data for data in processed_products.values() if 'title' in data]
        if logger:
            logger.info(f"Returned {len(cleaned_products)} products after cleaning.")
        return cleaned_products

    def quit(self):
        if self.logger:
            self.logger.info("Quitting driver.")
        self.driver.quit()

class CromaLocalScraper(CromaScraper):
    def __init__(self, logger, website: str):
        super().__init__(logger, website)

    def get_driver(self):
        if self.logger:
            self.logger.info("Initializing local Chrome driver.")
        options = webdriver.ChromeOptions()
        options.add_argument("--incognito")
        # options.add_argument("--headless")
        options.add_experimental_option(
            "prefs", {"profile.default_content_setting_values.geolocation": 2}
        )
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        self.driver = webdriver.Chrome(options=options)

class CromaServerScraper(CromaScraper):
    def __init__(self, logger, website: str):
        super().__init__(logger, website)

    def get_driver(self):
        if self.logger:
            self.logger.info("Initializing server Chrome driver.")
        options = webdriver.ChromeOptions()
        options.add_argument("--incognito")
        service = Service('/usr/bin/chromedriver') # type: ignore
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        options.add_experimental_option(
            "prefs", {"profile.default_content_setting_values.geolocation": 2}
        )
        options.add_argument("--user-data-dir=/tmp/chrome-user-data")
        options.add_argument("--headless") # Runs Chrome in headless mode.
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=options, service = service)

def run(target_machine: str, pincode: str | int, product_name: str, logger, website: str = "https://www.croma.com/"):
    cromaSc: CromaServerScraper | CromaLocalScraper
    if target_machine == 'local':
        cromaSc = CromaLocalScraper(logger, website)
    else:
        cromaSc = CromaServerScraper(logger, website)
    cromaSc.get_driver()

    location_success = cromaSc.change_location(str(pincode))
    if location_success:
        search_success = cromaSc.search_product(product_name)
        if search_success:
            products = cromaSc.scrape_product_details()
        else:
            products = []
    else:
        products = []
    cromaSc.quit()
    if products:
        products = cromaSc.clean_product_data(products, logger)
        return products

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
