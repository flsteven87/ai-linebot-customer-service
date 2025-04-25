"""
Logging configuration and utilities.
"""
import logging
import sys
from typing import Optional

def setup_logger(
    name: str, 
    level: int = logging.INFO, 
    format_str: Optional[str] = None
) -> logging.Logger:
    """
    Configure and return a logger with the given name and level.
    
    Args:
        name (str): Name of the logger.
        level (int): Logging level.
        format_str (Optional[str]): Format string for the logger.
            If None, a default format is used.
            
    Returns:
        logging.Logger: Configured logger.
    """
    if format_str is None:
        format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        
    formatter = logging.Formatter(format_str)
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    
    # Prevent duplicate logs
    logger.propagate = False
    
    return logger

# Default application logger
app_logger = setup_logger("app") 