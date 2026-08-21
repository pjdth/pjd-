import time

from pymilvus import MilvusClient, AnnSearchRequest, WeightedRanker

from atguigu.config.config import MilvusConfig
from atguigu.tool.logger import logger

milvus_client=None

def get_milvus_client():
    global milvus_client
    if milvus_client is not None:
        return milvus_client
    milvus_client=MilvusClient(
        uri=MilvusConfig.milvus_url
    )
    return milvus_client

def collection_exists(collection_name):
    """判断集合是否存在，供各节点在检索前做优雅降级（集合未创建时给友好提示而非报错）"""
    milvus_client = get_milvus_client()
    try:
        return milvus_client.has_collection(collection_name)
    except Exception as e:
        logger.error(f"检查集合 {collection_name} 是否存在失败: {e}")
        return False

def create_reqs(dense_data,sparse_data,limit=10,dense_anns_field=None,dense_param=None,sparse_anns_field=None,sparse_param=None,expr=None):
    if not dense_param:
        dense_param={
            "metric_type": "COSINE",
        }
    if not sparse_param:
        sparse_param={
            "metric_type": "IP",
        }
    # AnnSearchRequest.data 必须是「向量列表」，即使只查一条也要包成 [向量]
    # 否则稀疏向量(dict)传进去会触发 pymilvus 内部 req.data[0] 的 KeyError
    dense_req=AnnSearchRequest(
        data=[dense_data],
        anns_field=dense_anns_field,
        limit=limit,
        param=dense_param,
        expr=expr
    )
    sparse_req=AnnSearchRequest(
        data=[sparse_data],
        anns_field=sparse_anns_field,
        limit=limit,
        param=sparse_param,
        expr=expr
    )
    return [dense_req, sparse_req]

def search_hybrid(collection_name, reqs, ranker=(0.5, 0.5), limit=10, output_fields=None):
    milvus_client = get_milvus_client()

    weight_ranger = WeightedRanker(ranker[0], ranker[1], norm_score=True)
    results = milvus_client.hybrid_search(
        collection_name=collection_name,
        reqs=reqs,
        ranker=weight_ranger,
        limit=limit,
        output_fields=output_fields,
    )
    return results


def wait_indexes_ready(milvus_client, collection_name, index_names, timeout=120):
    """轮询等待指定索引构建完成。

    Milvus 建索引是异步的，create_collection/create_index 返回后索引可能仍在构建，
    此时 load_collection 会报 "no vector index on field: xxx"。必须在 load 前等索引 Finished。
    """
    start = time.time()
    for index_name in index_names:
        while True:
            desc = milvus_client.describe_index(collection_name, index_name)
            state = (desc or {}).get("state", "Unissued")
            if state == "Finished":
                break
            if state == "Failed":
                raise RuntimeError(f"集合 {collection_name} 的索引 {index_name} 构建失败")
            if time.time() - start > timeout:
                raise TimeoutError(f"等待索引 {index_name} 构建超时（{timeout}s）")
            time.sleep(1)
    return
