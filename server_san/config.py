



import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API key for Mistral
API_KEY = os.getenv("MISTRAL_API_KEY")

# MongoDB settings
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("MONGODB_DATABASE", "resume_automation")
USER_COLLECTION = os.getenv("MONGODB_USER_COLLECTION", "users")

# Email settings
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Paths configuration
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_PATH, os.getenv("LOGO_FILENAME", "Logo.png"))
BP = os.path.join(BASE_PATH, os.getenv("BP_FILENAME", "BP.jpeg"))
PROMPTS_DIR = os.path.join(BASE_PATH, os.getenv("PROMPTS_DIR", "Prompts"))
OUTPUT_DIR = os.path.join(BASE_PATH, os.getenv("OUTPUT_DIR", "Output"))
TEMPLATES_DIR = os.path.join(BASE_PATH, os.getenv("TEMPLATES_DIR", "templates"))
STATIC_DIR = os.path.join(BASE_PATH, os.getenv("STATIC_DIR", "static"))

# Create required directories
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PROMPTS_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# Global variables to store loaded skill matrix data
sheets_data = []
names_list = []