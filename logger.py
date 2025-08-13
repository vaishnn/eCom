import os
import logging

class logger:
    def __init__(self, directory: str = ".logs"):
        self.directory = directory

        pass
def setup_logger():
    """Sets up a logger to save logs to a file and print to console."""
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Get a logger instance
    logger = logging.getLogger('amazon_scraper')
    logger.setLevel(logging.INFO)

    # Prevent handlers from being added multiple times
    if logger.hasHandlers():
        logger.handlers.clear()

    # File handler to save logs to a file
    file_handler = logging.FileHandler('logs/scraper.log')
    file_handler.setLevel(logging.INFO)

    # Console handler to print logs to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Formatter to define the log message format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
