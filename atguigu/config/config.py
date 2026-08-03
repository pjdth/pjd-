import os

from dotenv import load_dotenv
load_dotenv(override=True)

class MineruConfig:
    mineru_token = os.getenv("MENERU_TOKEN")
    mineru_url = os.getenv("MENERU_URL")