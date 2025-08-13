from numpy import nan
from time import sleep
from random import uniform
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC

def get_driver() -> webdriver.Firefox:
    options = webdriver.FirefoxOptions()
    options.add_argument("--incognito")
    # options.add_argument("--headless")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)
    return driver

def search_product(driver: webdriver.Firefox, prduct_name: str) -> bool:
    try:
        driver.get("https://www.flipkart.com/")
        sleep(uniform(2, 4))
        search_bar = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="container"]/div/div[1]/div/div/div/div/div/div/div/div/div/div[1]/div/div/header/div[1]/div[2]/form/div/div/input'))
        )
        search_bar.click()
        sleep(uniform(1, 3))
        search_bar.send_keys(prduct_name)
        sleep(0.5)
        search_bar.send_keys(Keys.RETURN)
        sleep(uniform(2, 4))
        return True
    except Exception as e:
        print(f"Error searching product: {e}")
        return False

def scrape_product_details(driver: webdriver.Firefox, product: str) -> list:
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
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

driver = get_driver()
search_product(driver, "Iphone 16")
products = scrape_product_details(driver, "Iphone 16")
print(products)
