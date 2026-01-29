import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Freepik Configuration
FREEPIK_EMAIL = os.getenv("FREEPIK_EMAIL")
FREEPIK_PASSWORD = os.getenv("FREEPIK_PASSWORD")

# Envato Configuration
ENVATO_EMAIL = os.getenv("ENVATO_EMAIL")
ENVATO_PASSWORD = os.getenv("ENVATO_PASSWORD")

# Google Drive Configuration
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")

# Download Path
DOWNLOAD_PATH = os.path.join(os.getcwd(), "downloads")
