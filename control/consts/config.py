import os
from dotenv import load_dotenv

load_dotenv()

# Control variables
LOG_PATH = os.getenv('CONTROL_LOG_PATH')

# Formatter variables
FORMATTER_HOST = os.getenv('FORMATTER_HOST')
FORMATTER_CTRL_PORT = int(os.getenv('FORMATTER_CTRL_PORT'))
FORMATTER_LOG_PORT = int(os.getenv('FORMATTER_LOG_PORT'))

# Daemon variables
DAEMON_HOST = os.getenv('DAEMON_HOST')
DAEMON_CTRL_PORT = int(os.getenv('DAEMON_CTRL_PORT'))
DAEMON_LOG_PORT = int(os.getenv('DAEMON_LOG_PORT'))

# Model variables
MODEL_HOST = os.getenv('MODEL_HOST')
MODEL_CTRL_PORT = int(os.getenv('MODEL_CTRL_PORT'))
MODEL_LOG_PORT = int(os.getenv('MODEL_LOG_PORT'))
