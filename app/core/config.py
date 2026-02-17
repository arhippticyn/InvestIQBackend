from dotenv import load_dotenv
import os

load_dotenv()

DB_URL = os.getenv('DB_URL')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SEECRET = os.getenv('GOOGLE_CLIENT_SEECRET')
AUTH_EXP = os.getenv('AUTH_EXP')
ALGORITM = os.getenv('ALGORITM')
SECRET_KEY = os.getenv('SECRET_KEY')