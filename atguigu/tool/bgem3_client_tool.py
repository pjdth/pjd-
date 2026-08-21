import threading

from pymilvus.model.hybrid import BGEM3EmbeddingFunction

from atguigu.config.config import EmbeddingConfig
from atguigu.tool.json_tool import json_tool
from atguigu.tool.logger import logger

bge_m3_model=None
_model_lock = threading.Lock()
# encode 锁：单 GPU 模型全局只允许一个线程推理。
# 若多个线程同时对同一模型发起 CUDA 前向（encode_single_device 里还会 model.to(device) 遍历改写参数），
# 会触发 CUDA 并发初始化竞态/显存尖峰，Windows 上表现为原生段错误 0xC0000005 而非 Python 异常。
_encode_lock = threading.Lock()


def get_bge_m3_model():
    global bge_m3_model
    if bge_m3_model is not None:
        return bge_m3_model
    with _model_lock:
        # 双重检查锁：保证多线程并发时只有一个线程真正构造模型。
        # 若多个线程同时 BGEM3FlagModel(...)，会并发执行 from_pretrained，
        # 参数停留在 meta tensor 上，encode 时 .to(device) 报
        # "Cannot copy out of meta tensor; no data!"
        if bge_m3_model is None:
            bge_m3_model = BGEM3EmbeddingFunction(
                model_name=EmbeddingConfig.bge_m3_path,
                device=EmbeddingConfig.bge_device,
                use_fp16=EmbeddingConfig.bge_fp16  # 注意形参是 use_fp16，原 fp16 会被 **kwargs 忽略
            )
    return bge_m3_model


def get_bge_m3_embedding(texts: list[ str]):
    bge_m3_model = get_bge_m3_model()
    # 串行化 GPU 推理，避免多线程并发 encode 导致 CUDA 原生崩溃/显存溢出
    with _encode_lock:
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