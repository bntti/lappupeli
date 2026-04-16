import contextlib
import os

from dotenv import load_dotenv

dirname = os.path.dirname(__file__)
with contextlib.suppress(FileNotFoundError):
    load_dotenv(dotenv_path=os.path.join(dirname, "..", ".env"))

URL = os.getenv("DATABASE_URL")

SECRET_KEY = os.getenv("SECRET_KEY")
