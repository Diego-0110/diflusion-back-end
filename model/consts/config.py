import os
from dotenv import load_dotenv

load_dotenv()

# Model variables
HOST = os.getenv('MODEL_HOST')
CTRL_PORT = int(os.getenv('MODEL_CTRL_PORT'))
LOG_PORT = int(os.getenv('MODEL_LOG_PORT'))
LOG_PATH = os.getenv('MODEL_LOG_PATH')
PREDS_PATH = os.getenv('MODEL_PREDS_PATH')

# Database
MODEL_DB_URL = os.getenv('MODEL_DB_URL')
MODEL_DB_NAME = os.getenv('MODEL_DB_NAME')
WEB_DB_URL = os.getenv('WEB_DB_URL')
WEB_DB_NAME = os.getenv('WEB_DB_NAME')
HISTORY_DB_URL = os.getenv('HISTORY_DB_URL')
HISTORY_DB_NAME = os.getenv('HISTORY_DB_NAME')