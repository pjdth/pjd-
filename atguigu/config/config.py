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

class MinIoConfig:
    minio_endpoint = os.getenv('MINIO_ENDPOINT')
    minio_access_key = os.getenv('MINIO_ACCESS_KEY')
    minio_secret_key = os.getenv('MINIO_SECRET_KEY')
    minio_bucket_name = os.getenv('MINIO_BUCKET_NAME')
    minio_img_dir = os.getenv('MINIO_IMG_DIR')

class EmbeddingConfig:
    bge_m3_path=os.getenv("BGE_M3_PATH")
    bge_m3=os.getenv("BGE_M3")
    bge_device=os.getenv("BGE_DEVICE")
    # 特殊处理：将.env中的1/0转为布尔值，兼容常见的数字/字符串格式
    bge_fp16=os.getenv("BGE_FP16") in ("1", "True", "true", 1)

class MilvusConfig:
    milvus_url=os.getenv("MILVUS_URL")
    chunks_collection=os.getenv("CHUNKS_COLLECTION")
    item_name_collection=os.getenv("ITEM_NAME_COLLECTION")

class MongoConfig:
    mongo_url=os.getenv("MONGO_URL")
    mongo_db_name=os.getenv("MONGO_DB_NAME")

class McpConfig:
    mcp_base_url=os.getenv("MCP_DASHSCOPE_BASE_URL")
    api_key=os.getenv("OPENAI_API_KEY")

class RerankConfig:
    rerank_base_url = os.getenv("RERANK_BASE_URL")
    rerank_api_key = os.getenv("OPENAI_API_KEY")

class TtsConfig:
    """文字转语音配置（edge-tts 系统音色 + DashScope 声音复刻自定义音色）"""
    dashscope_base_url = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/api/v1")
    # 声音复刻使用的非实时 TTS 模型（qwen-voice-enrollment 创建音色时 target_model 需与之一致）
    clone_model = os.getenv("TTS_CLONE_MODEL", "qwen3-tts-vc-2026-01-22")
    api_key = os.getenv("OPENAI_API_KEY")