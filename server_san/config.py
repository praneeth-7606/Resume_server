import os

# API key for Mistral
API_KEY = "QsIe8weZaSTfNx9ykWlbjC3vGhWVSzWE"

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