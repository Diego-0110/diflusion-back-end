import os
from dotenv import load_dotenv

load_dotenv()

# Formatter variables
HOST = os.getenv('FORMATTER_HOST')
CTRL_PORT = int(os.getenv('FORMATTER_CTRL_PORT'))
LOG_PORT = int(os.getenv('FORMATTER_LOG_PORT'))

# Input/Output file paths
INPUT_PATH = os.getenv('INPUT_PATH')
OUTPUT_PATH = os.getenv('OUTPUT_PATH')

# Wheather API
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')