from dotenv import load_dotenv
from os import getenv
from time import sleep
from random import uniform
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

class CromaScraper:
    def __init__(self, website: str):
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
            return True
        except Exception as e:
            print(e)
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
            return True
        except Exception as e:
            print(e)
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
        return product_details

class CromaLocalScraper(CromaScraper):
    def __init__(self, website = "https://www.croma.com/"):
        super().__init__(website)

    def get_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--incognito")
        # options.add_argument("--headless")?
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        self.driver = webdriver.Chrome(options=options)

class CromaServerScraper(CromaScraper):
    def __init__(self, website: str):
        super().__init__(website)

    def get_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--incognito")
        service = Service('/usr/bin/chromedriver') # type: ignore
        options.add_argument("--user-data-dir=/tmp/chrome-user-data")
        options.add_argument("--headless") # Runs Chrome in headless mode.
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=options, service = service)
