import os
import logging
from logging.handlers import RotatingFileHandler

class RunIDFormatter(logging.Formatter):
    """Custom logging formatter that ensures run_id is always present in the log format."""
    def format(self, record):
        if not hasattr(record, "run_id"):
            record.run_id = "-"
        return super().format(record)

class RunLoggerAdapter(logging.LoggerAdapter):
    """Logger adapter that injects run_id into the extra context of all log messages."""
    def process(self, msg, kwargs):
        extra = dict(self.extra or {})
        if "extra" in kwargs:
            extra.update(kwargs["extra"])
        kwargs["extra"] = extra
        return msg, kwargs

def setup_logging():
    """Initializes and configures the namespaced 'sipher' logger.
    
    Prevents root propagation to avoid double logging under uvicorn, and
    guards against registering duplicate handlers on uvicorn --reload.
    """
    logger = logging.getLogger("sipher")
    logger.propagate = False
    
    # Configure logging level from environment
    log_level_str = os.environ.get("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    logger.setLevel(log_level)
    
    # Guard against duplicate handlers on uvicorn reload
    if not logger.handlers:
        os.makedirs("logs", exist_ok=True)
        
        formatter = RunIDFormatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s [run_id: %(run_id)s] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # 1. Console StreamHandler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 2. RotatingFileHandler for all app logs (5MB size limit, 5 backups)
        app_file_handler = RotatingFileHandler(
            "logs/app.log",
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        )
        app_file_handler.setLevel(log_level)
        app_file_handler.setFormatter(formatter)
        logger.addHandler(app_file_handler)
        
        # 3. RotatingFileHandler for ERROR level logs only
        error_file_handler = RotatingFileHandler(
            "logs/errors.log",
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        )
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(formatter)
        logger.addHandler(error_file_handler)

def get_logger(name: str):
    """Returns a namespaced logger under the 'sipher' namespace."""
    if name.startswith("sipher"):
        return logging.getLogger(name)
    return logging.getLogger(f"sipher.{name}")

def get_run_logger(name: str, run_id: str):
    """Returns a RunLoggerAdapter that injects run_id into every log line."""
    logger = get_logger(name)
    return RunLoggerAdapter(logger, {"run_id": run_id})
