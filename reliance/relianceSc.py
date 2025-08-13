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
    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.geolocation": 2
    })
    # options.add_argument("--headless")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def change_location(driver: webdriver.Chrome, pincode: str) -> bool:
    try:
        driver.get("https://www.reliancedigital.in/")
    except Exception:
        print("Error occurred while navigating to Reliance Digital")
        return False
    sleep(uniform(2, 4))
    try:
        updates_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'wzrk-cancel'))
        )
        if updates_button: #type: ignore
            updates_button.click()
            sleep(uniform(2, 4))
        pick_location = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="address-pincode-button"]/span'))
        )
        pick_location.click()
        sleep(uniform(2, 4))
    except Exception:
        print("Error occurred while finding location bar")
        return False
    try:
        pincode_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="input-pincode"]'))
        )
        pincode_input.send_keys(pincode)
        sleep(0.2)
        pincode_input.send_keys(Keys.ENTER)
        sleep(uniform(2, 4))
        return True
    except Exception as e:
        print(f"Error occurred while changing location to {pincode}: {e}")
        return False

def search_product(driver: webdriver.Chrome, product_name: str) -> bool:
    try:
        search_bar = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div[1]/div[2]/div/div/div[1]/input'))
        )
        search_bar.click()
        sleep(uniform(1, 2))
        search_bar.send_keys(product_name)
        sleep(0.4)
        search_bar.send_keys(Keys.ENTER)
        return True
    except Exception:
        print(f"Error occurred while searching for product {product_name}")
        return False

def scrape_product_details(driver: webdriver.Chrome) -> list:
    sleep(uniform(2, 4))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
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
    return list_products

driver = get_driver()
change_location(driver, "226030")
search_product(driver, "iPhone 16")
print(scrape_product_details(driver))
