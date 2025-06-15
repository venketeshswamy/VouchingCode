# ocr_tool_qt/utils/logger.py

import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger():
    """
    Configures and returns a centralized logger for the application.
    """
    log_directory = "logs"
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    log_file = os.path.join(log_directory, "app.log")

    # Create logger
    logger = logging.getLogger("OCRToolLogger")
    logger.setLevel(logging.INFO)

    # Prevent adding multiple handlers if function is called more than once
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create handlers
    # Console handler
    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.INFO)

    # File handler (rotates logs)
    f_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024, # 10 MB
        backupCount=5
    )
    f_handler.setLevel(logging.INFO)

    # Create formatters and add it to handlers
    log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(log_format)
    f_handler.setFormatter(log_format)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger

# Create a single logger instance to be used across the application
log = setup_logger()

