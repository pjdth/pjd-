from pymilvus import MilvusClient

from atguigu.config.config import MilvusConfig

milvus_client=None

def get_milvus_client():
    global milvus_client
    if milvus_client is not None:
        return milvus_client
    milvus_client=MilvusClient(
        uri=MilvusConfig.milvus_url
    )
    return milvus_client