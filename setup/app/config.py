import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()


# values will be taken from environment variables, usually defined in .env file or via secret management in deployment
DB_URL = os.getenv("DB_URL")
REDIS_URL = os.getenv("REDIS_URL")
RABBIT_URL = os.getenv("RABBIT_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
