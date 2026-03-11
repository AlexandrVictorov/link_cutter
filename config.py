from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST=os.environ.get("DB_HOST")
DB_PORT=os.environ.get("DB_PORT")
DB_NAME=os.environ.get("DB_NAME")
DB_USER=os.environ.get("DB_USER")
DB_PASS=os.environ.get("DB_PASS")

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

SECRET_KEY=os.environ.get("SECRET_KEY")

RESET_PASSWORD_SECRET=os.environ.get("RESET_PASSWORD_SECRET")

SMTP_HOST=os.environ.get("SMTP_HOST")
SMTP_PORT=os.environ.get("SMTP_PORT")
SMTP_USER=os.environ.get("SMTP_USER")
SMTP_PASSWORD=os.environ.get("SMTP_PASSWORD")