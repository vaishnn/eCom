from websites.amazon.amazonSc import AmazonLocalScraper, AmazonServerScraper
from websites.croma.cromaSc import CromaLocalScraper, CromaServerScraper
from websites.flipkart.flipkartSc import FlipkartLocalScraper, FlipkartServerScraper
from websites.reliance.relianceSc import RelianceLocalScraper, RelianceServerScraper

from dotenv import load_dotenv
from os import getenv
import time
from yaml import safe_load, YAMLError
import pymysql

load_dotenv()

def load_config(config: str):
    pass



def main():

    pass
