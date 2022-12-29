from dotenv import load_dotenv
import os



load_dotenv()


DB_NAME = os.getenv('DB_NAME')
TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
PRIZE_URL = os.getenv('PRIZE_URL')
