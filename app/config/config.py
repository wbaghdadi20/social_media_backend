import os
from dotenv import load_dotenv

# Load environment variables from .env file (if present)
load_dotenv()

def get_env_variable(name):
    value = os.getenv(name)
    if value is None:
        raise ValueError(f"Missing required environment variable: {name}")
    return value

SQLALCHEMY_DATABASE_URL = get_env_variable("SQLALCHEMY_DATABASE_URL")
SECRET_KEY = get_env_variable("SECRET_KEY")
ALGORITHM = get_env_variable("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(get_env_variable("ACCESS_TOKEN_EXPIRE_MINUTES"))
