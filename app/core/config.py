from dotenv import load_dotenv
import os

load_dotenv()

DB_URL = os.getenv('DB_URL')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
AUTH_EXP = os.getenv('AUTH_EXP')
ALGORITM = os.getenv('ALGORITM')
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG')