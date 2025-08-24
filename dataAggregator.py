from dotenv import load_dotenv
import yaml
from logger import ExtensiveLogger
import os
import sys
import smtplib
from email.mime.text import MIMEText
import pymysql
from datetime import date
load_dotenv()
from websites.amazon import amazonSc
from websites.croma import cromaSc
from websites.flipkart import flipkartSc
from websites.reliance import relianceSc


class DataAggregator:
    """
    DataAggregator class for aggregating data from a database and sending email notifications.

    Attributes:
        db_config (dict): Configuration for the database connection.
        email_config (dict): Configuration for the email notification.
        logger (logging.Logger): Logger instance for logging messages.
    """
    def __init__(self, db_config: dict, email_config: dict, logger):
        self.db_config = db_config
        self.email_config = email_config
        self.logger = logger

    def send_email(self, subject, body):
        """
        Sends an email notification.
        """
        try:
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = self.email_config['sender']
            msg['To'] = self.email_config['recipient']

            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['username'], self.email_config['password'])
                server.send_message(msg)
            self.logger.info(f"Email sent successfully: '{subject}'")
        except Exception as e:
            self.logger.error(f"Failed to send email. Error: {e}")

    def get_db_connection(self):
        try:
            connection = pymysql.connect(**self.db_config)
            self.logger.info("Database connection successful.")
            return connection
        except pymysql.MySQLError as e:
            self.logger.error(f"Database connection failed: {e}")
            return None

    def setup_database(self):
        conn = self.get_db_connection()
        if not conn:
            return

        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS products (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        title VARCHAR(255) NOT NULL,
                        price INT NOT NULL,
                        platform VARCHAR(50) NOT NULL,
                        scrape_date DATE NOT NULL,
                        city VARCHAR(50) NOT NULL,
                        pincode VARCHAR(10) NOT NULL,
                        UNIQUE KEY unique_product (title, platform, scrape_date, city, pincode)
                    )
                """)
            conn.commit()
            self.logger.info("Database table 'products' is ready.")
        except pymysql.MySQLError as e:
            self.logger.error(f"Failed to create or verify table: {e}")
        finally:
            conn.close()

    def process_platform_data(self, platform_name, raw_data, pincode, city):
        self.logger.info(f"Processing data for platform: {platform_name}")
        try:
            today = date.today()
            conn = self.get_db_connection()
            if not raw_data:
                self.logger.warning(f"No data to process for platform: {platform_name}")
                return
            if not conn:
                self.logger.error("Database connection failed.")
                return
            try:
                with conn.cursor() as cursor:
                    query = """
                        INSERT INTO products (title, price, platform, pincode, city, scrape_date)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    data_to_insert = [
                        (item['title'], item['price'], platform_name,pincode, city, today)
                        for item in raw_data
                    ]
                    cursor.executemany(query, data_to_insert)
                conn.commit()
                self.logger.info(f"Data for platform {platform_name} processed successfully.")
                subject = f"Data processed--{platform_name}--"
                message = f"Data for platform {platform_name} has been processed successfully."
                self.send_email(subject, message)
            except pymysql.MySQLError as e:
                self.logger.error(f"Failed to process data for platform {platform_name}: {e}")
        except pymysql.MySQLError as e:
            self.logger.error(f"Database connection failed: {e}")
        finally:
            conn.close() # type: ignore

def read_yaml(logger, yaml_file_path: str) -> dict:
    try:
        with open(yaml_file_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        logger.error(f"YAML file not found: {yaml_file_path}")
        return {}
    except yaml.YAMLError:
        logger.error(f"Error parsing YAML file: {yaml_file_path}")
        return {}



if __name__ =="__main__":
    to_run = []
    if len(sys.argv) > 1:
        _to_run: str = sys.argv[1].strip().lower()

        if _to_run == 'all':
            to_run = ['amazon', 'flipkart', 'croma']
        else:
            if 'amazon' in _to_run:
                to_run.append('amazon')
            if 'flipkart' in _to_run:
                to_run.append('flipkart')
            if 'croma' in _to_run:
                to_run.append('croma')
    else:
        to_run = ['amazon', 'flipkart', 'croma']

    target_machine = str(os.getenv('TARGET_MACHINE'))
    logger_wrapper = ExtensiveLogger('scraper.log', max_bytes=10000000, backup_count=3)
    logger = logger_wrapper.get_logger()
    logger.info("Logger initialized.")
    logger.info("This is the first log message.")

    __DB_CONFIG = {
            'host': os.getenv('DB_HOST'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'database': os.getenv('DB_NAME'),
            'cursorclass': pymysql.cursors.DictCursor
        }
    __EMAIL_SETTINGS = {
        'smtp_server': os.getenv('SMTP_SERVER'),
        'smtp_port': os.getenv('SMTP_PORT'),
        'username': os.getenv('FROM_EMAIL'),
        'password': os.getenv('SMTP_PASSWORD'),
        'sender': os.getenv('FROM_EMAIL'),
        'recipient': os.getenv('TO_EMAIL')
    }
    schema = read_yaml(logger, 'schema.yaml')
    pincodes = schema.get('pincodes', {})
    products = schema.get('products', [])
    aggregator = DataAggregator(__DB_CONFIG, __EMAIL_SETTINGS, logger)
    aggregator.setup_database()
    for product in products:
        flipkart_done: bool = False
        for city in pincodes:
            pincode = pincodes[city]

            if target_machine == "local":
                # Reliance
                logger.info(f"---Processing product {product} for pincode {pincode} for platform Reliance---")
                relianceData = relianceSc.run(target_machine, pincode, product, logger) #type: ignore
                aggregator.process_platform_data("Reliance", relianceData, pincode, city)
                logger.info("Reliance data processed successfully finished.")
            else:
                if 'amazon' in to_run:
                    # Amazon
                    logger.info(f"---Processing product {product} for pincode {pincode} for platform Amazon---")
                    amazonData = amazonSc.run(target_machine, pincode, product, logger)
                    aggregator.process_platform_data("Amazon", amazonData, pincode, city)
                    logger.info("Amazon data processed successfully finished.")


                # Flipkart
                if 'flipkart' in to_run:
                    if flipkart_done is False:
                        logger.info(f"---Processing product {product} for pincode {pincode} for platform Flipkart---")
                        flipkartData = flipkartSc.run(target_machine, pincode, product, logger)
                        aggregator.process_platform_data("Flipkart", flipkartData, pincode, city)
                        logger.info("Flipkart data processed successfully finished.")
                        flipkart_done = True

                # Croma
                if 'croma' in to_run:
                    logger.info(f"---Processing product {product} for pincode {pincode} for platform Croma---")
                    cromaData = cromaSc.run(target_machine, pincode, product, logger)
                    aggregator.process_platform_data("Croma", cromaData, pincode, city)
                    logger.info("Croma data processed successfully finished.")

    logger.info("Finished processing all platforms.")
