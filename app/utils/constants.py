from decouple import config

# Database configuration
MYSQL_SERVER = config("MYSQL_SERVER", default="localhost")
MYSQL_USER = config("MYSQL_USER")
MYSQL_PASSWORD = config("MYSQL_PASSWORD")
MYSQL_DATABASE = config("MYSQL_DATABASE")


ENVIRONMENT= config("ENVIRONMENT", default="dev")

if ENVIRONMENT == "dev":
    DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_SERVER}:3306/{MYSQL_DATABASE}"
    print(DATABASE_URL)
elif ENVIRONMENT == "prod":
    DATABASE_URL = config("DATABASE_URL")

# Token configuration
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
SECRET_KEY = config("SECRET_KEY")


SERVER_NAME: str = "Lost and Found Management System"
API_V1_STR: str = "/v1"
API_ROOT_PATH= "/api" if ENVIRONMENT == "prod" else "/"