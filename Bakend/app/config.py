import os
from dotenv import load_dotenv
 
load_dotenv()
 
MOODLE_URL = os.getenv("MOODLE_URL", "http://localhost:8080")
MOODLE_TOKEN = os.getenv("MOODLE_TOKEN", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
 
if not MOODLE_TOKEN:
    print("⚠️  ADVERTENCIA: MOODLE_TOKEN no está configurado en el .env")
 
if not GEMINI_API_KEY:
    print("⚠️  ADVERTENCIA: GEMINI_API_KEY no está configurado en el .env")