from pymilvus.model.hybrid import BGEM3EmbeddingFunction

from atguigu.config.config import EmbeddingConfig
from atguigu.tool.json_tool import json_tool
from atguigu.tool.logger import logger

bge_m3_model=None

def get_bge_m3_model():
    global bge_m3_model
    if not bge_m3_model:
        bge_m3_model = BGEM3EmbeddingFunction(
            model_name=EmbeddingConfig.bge_m3_path,
            device=EmbeddingConfig.bge_device,
            fp16=EmbeddingConfig.bge_fp16
        )
    return bge_m3_model

def get_bge_m3_embedding(texts:list[ str]):
    bge_m3_model = get_bge_m3_model()
    embeddings=bge_m3_model.encode_documents( texts)
    # dense: numpy 二维数组 -> list[list[float]]（Milvus 稠密向量字段要求的格式）
    dense = [row.tolist() for row in embeddings["dense"]]
    # sparse: scipy 稀疏矩阵列表 -> list[{token_id: weight}]（Milvus 稀疏向量字段要求的格式）
    sparse = []
    for row in embeddings["sparse"]:
        sparse.append({int(idx): float(w) for idx, w in zip(row.indices, row.data)})
    return {
        "dense": dense,
        "sparse": sparse
    }

if __name__ == '__main__':
    logger.info(json_tool(get_bge_m3_embedding(['大狗叫','哈吉米'])))