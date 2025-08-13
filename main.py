from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
import smtplib
import pymysql
from pymysql.cursors import DictCursor
import datetime
import os
import pandas as pd
from dotenv import load_dotenv

from yaml import safe_load, YAMLError

class MainBridge:
    def __init__(self, yamlfile: str = "schema.yaml"):
        load_dotenv()
        self.schema: dict
        self.__EMAIL_CONFIG: dict
        self.__DB_CONFIG: dict
        self.connection: pymysql.Connection
        self.cursor: DictCursor
        self.PINCODES: list
        self.PRODUCTS: list
        self.schema = self.__load_yaml(yamlfile)
        self.__EMAIL_CONFIG = self.__load_email_config()
        self.__DB_CONFIG = self.__load_db_config()

        self.PINCODES, self.PRODUCTS = self.__load_pincode_and_products()

    def __load_yaml(self, yamlfile) -> dict:
        if yamlfile is not None:
            try:
                with open(yamlfile, "r") as file:
                    return safe_load(file)
            except FileNotFoundError:
                print(f"File {yamlfile} not found.")
            except YAMLError as e:
                print(f"Error loading YAML file: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")
        return {}

    def __create_table(self):
        pass

    def __load_pincode_and_products(self):
        try:
            print(self.schema)
            pincode = self.schema["pincodes"]
            products = self.schema["products"]
            return pincode, products
        except Exception as e:
            print(f"Error loading pincode and products: {e}")
            raise

    def __load_db_config(self):
        try:
            return {
                'host': str(os.getenv('DB_HOST')),
                'user': str(os.getenv('DB_USER')),
                'password': str(os.getenv('DB_PASSWORD')),
                'database': str(os.getenv('DB_NAME')),
                'port': os.getenv('DB_PORT')
            }
        except Exception as e:
            print(f"Error loading database config: {e}")
            raise

    def __load_email_config(self):
        try:
            return {
                'smtp_server': str(os.getenv('SMTP_SERVER')),
                'smtp_port': os.getenv('SMTP_PORT'),
                'sender_password': str(os.getenv('SMTP_PASSWORD')),
                'sender_email': str(os.getenv('FROM_EMAIL')),
                'receiver_email': str(os.getenv('TO_EMAIL'))
            }
        except Exception as e:
            print(f"Error loading email config: {e}")
            raise

    def __send_email(self,subject: str ,body: str) -> None:
        msg = MIMEMultipart()
        msg['From'] = self.__EMAIL_CONFIG['sender_email']
        msg['To'] = self.__EMAIL_CONFIG['receiver_email']
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP(self.__EMAIL_CONFIG['smtp_server'], self.__EMAIL_CONFIG['smtp_port']) as server:
                server.starttls()
                server.login(self.__EMAIL_CONFIG['sender_email'], self.__EMAIL_CONFIG['sender_password'])
                server.send_message(msg)
            print("Email Notification Send Successfully")
        except Exception as e:
            print(f"Error sending email: {e}")


    def __connect_to_db(self):
        try:
            self.connection = pymysql.connect(
                host=self.__DB_CONFIG['host'],
                user=self.__DB_CONFIG['user'],
                password=self.__DB_CONFIG['password'],
                database=self.__DB_CONFIG['database'],
                port=int(self.__DB_CONFIG['port'])
            )
            print("Connected to Database Successfully")
        except Exception as e:
            print(f"Error connecting to database: {e}")

    def _update_table(self):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT * FROM table_name")
                result = cursor.fetchall()
                print(result)
        except Exception as e:
            print(f"Error updating table: {e}")
