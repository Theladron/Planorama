from app.core.config_loader import settings
import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = (
    f"postgresql+psycopg2://"
    f"{settings.POSTGRESQL_USERNAME}:"
    f"{settings.POSTGRESQL_PASSWORD}@"
    f"{settings.POSTGRESQL_SERVER}:"
    f"{settings.POSTGRESQL_PORT}/"
    f"{settings.POSTGRESQL_DATABASE}"
)
print("DB_URL =", repr(DB_URL))


print(os.getenv("DB_URI"))