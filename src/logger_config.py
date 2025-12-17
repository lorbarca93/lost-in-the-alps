"""
Logging configuration for Lost in the Alps scrapers
"""

import logging
import sys
from pathlib import Path

def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Configure and return a logger for the scraper
    
    Args:
        name: Logger name (usually __name__ from the calling module)
        level: Logging level (default: INFO)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Don't add handlers if they already exist
    if logger.handlers:
        return logger
    
    # Console handler with formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Format: [INFO] scraper_name: Message
    formatter = logging.Formatter(
        '[%(levelname)s] %(name)s: %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger

def setup_file_logger(name: str, log_file: str = None, level: int = logging.DEBUG) -> logging.Logger:
    """
    Configure logger with both console and file output
    
    Args:
        name: Logger name
        log_file: Path to log file (default: logs/{name}.log)
        level: Logging level (default: DEBUG for file)
    
    Returns:
        Configured logger instance
    """
    logger = setup_logger(name, logging.INFO)
    
    # Create logs directory if needed
    logs_dir = Path(__file__).parent / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    # Default log file path
    if log_file is None:
        log_file = logs_dir / f"{name.replace('.', '_')}.log"
    
    # File handler with more detailed formatting
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    
    # Format: timestamp [LEVEL] logger_name: Message
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    logger.addHandler(file_handler)
    
    return logger
