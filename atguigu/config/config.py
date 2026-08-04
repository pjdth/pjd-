import os

from dotenv import load_dotenv
env_path =os.path.abspath(os.path.join(os.path.dirname(__file__), '../../.env'))
load_dotenv(override=True,dotenv_path=env_path)

class MineruConfig:
    mineru_token = os.getenv("MINERUN_TOKEN")
    mineru_url = os.getenv("MINERU_BASE_URL")

class LLMConfig:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_api_base = os.getenv("OPENAI_API_BASE")
    llm_default_model = os.getenv("LLM_DEFAULT_MODEL")
    llm_default_temperature = float(os.getenv("LLM_DEFAULT_TEMPERATURE"))
    vl_model = os.getenv("VL_MODEL")
    item_model = os.getenv("ITEM_MODEL")