import logging                                   # Built-in logging module
import os                                        # For file and path management
from logging.handlers import TimedRotatingFileHandler  # For rotating log files
from pythonjsonlogger import jsonlogger         # External package for JSON-formatted logs

# --- Define and ensure log directory exists ---
LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')  # logs/ at root
os.makedirs(LOG_DIR, exist_ok=True)

# --- Define file paths for access and error logs ---
ACCESS_LOG_PATH = os.path.join(LOG_DIR, 'access.log')  # For all info-level logs
ERROR_LOG_PATH = os.path.join(LOG_DIR, 'error.log')    # For error/exception logs

# --- Logger factory function ---
def get_logger(name: str = "notation_logger") -> logging.Logger:
    """
    Returns a logger that writes JSON-formatted logs to separate files:
    - error.log for ERROR, WARNING, CRITICAL activity
    - access.log for INFO, DEBUG activity
    """
    # --- Create main logger that processes all logs ---
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Root level set to DEBUG so all logs are processed

    # Avoid re-adding handlers if already configured
    if not logger.handlers:
        # --- Create JSON formatter ---
        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(levelname)s %(name)s %(message)s'  # Standard fields + message as JSON
        )

        # --- Access Log Handler: rotate daily, keep forever ---
        access_handler = TimedRotatingFileHandler(
            ACCESS_LOG_PATH, when="midnight", interval=1, backupCount=0  # keep logs indefinitely
        )
        access_handler.setLevel(logging.INFO)  # Capture INFO, DEBUG and lower levels
        access_handler.setFormatter(formatter)

        # --- Error Log Handler: rotate daily, keep forever ---
        error_handler = TimedRotatingFileHandler(
            ERROR_LOG_PATH, when="midnight", interval=1, backupCount=0  # keep logs indefinitely
        )
        error_handler.setLevel(logging.ERROR)  # Capture ERROR, WARNING, CRITICAL levels
        error_handler.setFormatter(formatter)

        # --- Add handlers to logger ---
        logger.addHandler(access_handler)
        logger.addHandler(error_handler)

    return logger

