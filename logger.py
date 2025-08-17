from io import TextIOWrapper
import logging
import os
import glob
from logging.handlers import RotatingFileHandler
from datetime import datetime

class ExtensiveLogger:
    """
    A logger class for extensive logging that manages old log files.

    This logger will create a log file and rotate it when it reaches a
    certain size. When a rotation occurs, the old log file is moved to
    a '.old_logs' directory. The most recent log file always stays in the
    main directory.
    """

    def __init__(self, log_file_name='app.log', log_dir='.', old_logs_dir='.old_logs', max_bytes=1024*1024, backup_count=5):
        """
        Initializes the ExtensiveLogger.

        Args:
            log_file_name (str): The name of the log file.
            log_dir (str): The directory where the log file will be stored.
            old_logs_dir (str): The directory where old logs will be archived.
            max_bytes (int): The maximum size of the log file in bytes before rotation.
            backup_count (int): The number of backup files to keep.
        """
        self.log_dir = log_dir
        self.log_file_path = os.path.join(log_dir, log_file_name)
        self.old_logs_path = os.path.join(log_dir, old_logs_dir)
        self.max_bytes = max_bytes
        self.backup_count = backup_count

        # Create the directory for old logs if it doesn't exist
        if not os.path.exists(self.old_logs_path):
            os.makedirs(self.old_logs_path)

        # Configure the logger
        self.logger = logging.getLogger('extensive_logger')
        self.logger.setLevel(logging.DEBUG)

        # Create a custom rotating file handler
        self.handler = self.CustomRotatingFileHandler(
            self.log_file_path,
            old_logs_dir=self.old_logs_path,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count
        )

        # Create a formatter and set it for the handler
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.handler.setFormatter(formatter)

        # Add the handler to the logger
        if not self.logger.handlers:
            self.logger.addHandler(self.handler)
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            console_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)

    def get_logger(self):
        """Returns the configured logger instance."""
        return self.logger

    class CustomRotatingFileHandler(RotatingFileHandler):
        """
        A custom rotating file handler to move old logs to a specific directory.
        """
        def __init__(self, filename, old_logs_dir, **kwargs):
            self.old_logs_dir = old_logs_dir
            super().__init__(filename, **kwargs)

        def doRollover(self):
            """
            Performs the log file rollover.

            When this method is called, it renames the existing log file with a
            timestamp and moves it to the '.old_logs' directory.
            """
            if self.stream:
                self.stream.close()
                self.stream: TextIOWrapper

            # Generate a timestamped name for the old log file
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            dfn = os.path.join(self.old_logs_dir, f"{os.path.basename(self.baseFilename)}.{timestamp}")

            # Rename the current log file and move it
            if os.path.exists(self.baseFilename):
                os.rename(self.baseFilename, dfn)

            # Clean up older logs if they exceed the backup count
            self._cleanup_old_logs()

            if not self.delay:
                self.stream = self._open()

        def _cleanup_old_logs(self):
            """
            Deletes the oldest log files if the number of backups exceeds the limit.
            """
            log_files = glob.glob(os.path.join(self.old_logs_dir, f"{os.path.basename(self.baseFilename)}.*"))
            if len(log_files) > self.backupCount:
                log_files.sort(key=os.path.getmtime)
                for f in log_files[:-self.backupCount]:
                    os.remove(f)


# --- Example Usage ---
if __name__ == '__main__':
    # Initialize the logger
    # Using a small max_bytes for demonstration purposes to see rotation happen quickly.
    logger_wrapper = ExtensiveLogger('scraper.log', max_bytes=10000000, backup_count=3)
    log = logger_wrapper.get_logger()

    log.info("Logger initialized.")
    log.info("This is the first log message.")

    # Simulate generating a lot of logs to trigger rotation
    for i in range(50):
        log.debug(f"This is a debug message number {i}. It adds some bytes to the log file.")
        log.info(f"Log entry {i}: Information message.")
        log.warning(f"Log entry {i}: A warning has occurred.")
        log.error(f"Log entry {i}: An error has been logged.")

    log.critical("This is a critical message after the loop.")
    print(f"Logging complete. Check 'my_app.log' and the '{logger_wrapper.old_logs_path}' directory.")
