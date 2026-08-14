from pymilvus import MilvusClient, AnnSearchRequest, WeightedRanker

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
