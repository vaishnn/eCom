from numpy import nan
from time import sleep
from random import uniform
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC

def get_driver() -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    # options.add_argument("--headless")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def search_product(driver: webdriver.Chrome, prduct_name: str) -> bool:
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

driver = get_driver()
search_product(driver, "Iphone 16")
