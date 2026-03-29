import logging
import os

def setup_logger(name="AetherVoice", log_level=logging.INFO):
    """Configures a professional logging system with error and performance files."""
    if not os.path.exists("logs"):
        os.makedirs("logs")

    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Console Handler
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    ch.setFormatter(formatter)
    
    # Error File Handler (UTF-8)
    eh = logging.FileHandler("logs/errors.log", encoding='utf-8')
    eh.setLevel(logging.ERROR)
    eh.setFormatter(formatter)
    
    # Performance/Activity Handler (UTF-8)
    ph = logging.FileHandler("logs/performance.log", encoding='utf-8')
    ph.setLevel(logging.INFO)
    ph.setFormatter(formatter)

    # Avoid duplicate handlers
    if not logger.handlers:
        logger.addHandler(ch)
        logger.addHandler(eh)
        logger.addHandler(ph)
    
    return logger
