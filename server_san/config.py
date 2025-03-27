import os

# API key for Mistral
API_KEY = "QsIe8weZaSTfNx9ykWlbjC3vGhWVSzWE"



import os
from datetime import timedelta

# Existing config settings
# TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
# STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
# OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "Output")
# PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "Prompts")

# MongoDB settings
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = "resume_automation"
USER_COLLECTION = "users"
EMAIL_SENDER = "praneethvvsss@gmail.com"  # Replace with your actual sender email
SMTP_SERVER = "smtp.gmail.com"  # Replace with your SMTP server
SMTP_PORT = 587  # Replace with your SMTP port
SMTP_USERNAME = "praneethvvsss@gmail.com"  # Replace with your SMTP username
SMTP_PASSWORD = "yxui hjzn tquj pjea"  # Replace with your SMTP password

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "123456789")  # Change this in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Paths configuration
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_PATH, "Logo.png")
BP = os.path.join(BASE_PATH, "BP.jpeg")
PROMPTS_DIR = os.path.join(BASE_PATH, "Prompts")
OUTPUT_DIR = os.path.join(BASE_PATH, "Output")
TEMPLATES_DIR = os.path.join(BASE_PATH, "templates")
STATIC_DIR = os.path.join(BASE_PATH, "static")

# Create required directories
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PROMPTS_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# Global variables to store loaded skill matrix data
sheets_data = []
names_list = []