# --- Configuration ---
import os
import logging
from langchain_ollama.chat_models import ChatOllama

# Get the absolute path of the project's root directory
# This assumes the script is in the 'src' directory.
# The root is one level up from the script's directory.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configuration constants
MODEL = "mistral"
DB_FILE = os.path.join(PROJECT_ROOT, "data", "sales.db")
DATABASE_PATH = DB_FILE  # Alias for compatibility
LOG_FILE = os.path.join(PROJECT_ROOT, "logs", "project.log")
CSV_FILE = os.path.join(PROJECT_ROOT, "data", "sales_data.csv")
CHART_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data")

# Configuration validation
def validate_configuration():
    """
    Validate the configuration settings and environment.
    Returns True if valid, False otherwise.
    """
    issues = []
    
    # Check if required directories exist or can be created
    required_dirs = [
        os.path.dirname(DB_FILE),
        os.path.dirname(LOG_FILE)
    ]
    
    for dir_path in required_dirs:
        try:
            os.makedirs(dir_path, exist_ok=True)
        except Exception as e:
            issues.append(f"Cannot create directory {dir_path}: {e}")
    
    # Check if CSV file exists (needed for database creation)
    if not os.path.exists(CSV_FILE):
        issues.append(f"Source CSV file not found: {CSV_FILE}")
    
    # Validate model name
    if not MODEL or not isinstance(MODEL, str):
        issues.append(f"Invalid model name: {MODEL}")
    
    # Log any issues
    if issues:
        for issue in issues:
            logging.warning(f"Configuration issue: {issue}")
        return False
    
    logging.info("Configuration validation passed")
    return True

# --- LLM Initialization with error handling ---
try:
    llm = ChatOllama(model=MODEL)
    logging.info(f"LLM initialized successfully with model: {MODEL}")
except Exception as e:
    logging.error(f"Failed to initialize LLM with model {MODEL}: {e}")
    raise Exception(f"LLM initialization failed: {e}")

# Validate configuration on import
if not validate_configuration():
    logging.warning("Configuration validation failed - some features may not work correctly")

# Export configuration summary for debugging
CONFIG_SUMMARY = {
    "model": MODEL,
    "project_root": PROJECT_ROOT,
    "db_file": DB_FILE,
    "log_file": LOG_FILE,
    "csv_file": CSV_FILE,
    "db_exists": os.path.exists(DB_FILE),
    "csv_exists": os.path.exists(CSV_FILE)
}

logging.info(f"Configuration loaded: {CONFIG_SUMMARY}")
