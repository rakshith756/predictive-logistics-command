import os
from dotenv import load_dotenv
load_dotenv()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'logistics.db')
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-change-me')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', '')
