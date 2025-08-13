import time
import random
import logging
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import json
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC

log_dir = ".log"
log_file = os.path.join(log_dir, "amazon_sc.log")

os.makedirs(log_dir, exist_ok=True)

logger = logging.getLogger("amazon_sc")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

handler = logging.FileHandler(log_file)
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_driver() -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    # options.add_argument("--headless")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    logger.info("Driver initialized")
    return driver

def change_location(driver: webdriver.Chrome, zip_code: str) -> bool:
    try:
        driver.get("https://www.amazon.in")
        time.sleep(random.uniform(2, 4))

        location_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "glow-ingress-block"))
        )
        location_button.click()
        time.sleep(random.uniform(2, 4))

        zip_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "GLUXZipUpdateInput"))
        )
        zip_input.send_keys(str(zip_code))
        time.sleep(random.uniform(2, 4))

        # apply_button = driver.find_elements(By.ID, "GLUXZipUpdate")
        # apply_button.click()
        apply_button = driver.find_element(By.ID, "GLUXZipUpdate")
        apply_button.click()
        time.sleep(random.uniform(2, 4))
        logger.info("Location changed to {}".format(zip_code))
        return True
    except Exception as e:
        logger.error(f"Could not change location to {zip_code}. Error: {e}")
        driver.quit()
        return False

def search_product(driver: webdriver.Chrome, product_name: str) -> bool:
    try:
        search_bar = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))
        )
        search_bar.clear()
        search_bar.send_keys(product_name)
        search_bar.send_keys(Keys.RETURN)
        time.sleep(random.uniform(2, 4))
        logger.info("Product search initiated for {}".format(product_name))
        return True
    except Exception as e:
        logger.error(f"Could not search for {product_name}. Error: {e}")
        driver.quit()
        return False

def scrape_product_details(driver: webdriver.Chrome) -> list:
    soup = BeautifulSoup(driver.page_source, 'html.parser')
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

if __name__ == "__main__":
    driver = get_driver()
    if change_location(driver, "226030"):
         if search_product(driver, "Iphone 16 "):
            products = scrape_product_details(driver)
            with open("test_am.json", "w") as f:
                json.dump(products, f)
    driver.quit()
