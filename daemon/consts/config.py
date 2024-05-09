import os
from dotenv import load_dotenv

load_dotenv()

# Daemon variables
HOST = os.getenv('DAEMON_HOST')
CTRL_PORT = int(os.getenv('DAEMON_CTRL_PORT'))
LOG_PORT = int(os.getenv('DAEMON_LOG_PORT'))
LOG_PATH = os.getenv('DAEMON_LOG_PATH')

# Input/Output file paths
OUTPUT_PATH = os.getenv('OUTPUT_PATH')

# Database
MODEL_DB_URL = os.getenv('MODEL_DB_URL')
MODEL_DB_NAME = os.getenv('MODEL_DB_NAME')
WEB_DB_URL = os.getenv('WEB_DB_URL')
WEB_DB_NAME = os.getenv('WEB_DB_NAME')
