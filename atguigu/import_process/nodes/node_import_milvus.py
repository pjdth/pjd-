import json
import threading
from pathlib import Path

from pymilvus import DataType

from atguigu.config.config import MilvusConfig
from atguigu.import_process.base import NodeBase
from atguigu.import_process.state import ImportGraphState
from atguigu.tool.json_tool import json_tool
from atguigu.tool.logger import logger
from atguigu.tool.milvus_client_tool import milvus_client, get_milvus_client, wait_indexes_ready

# 全局建表锁：多个上传任务并发执行时，串行化 chunks 集合的“检查+建表+等索引”流程，
# 避免重复建表或索引未就绪就 load 报错（no vector index on field: sparse_vector）
_chunks_collection_lock = threading.Lock()


class NodeImportMilvus(NodeBase):
    """
    导入向量库节点：数据持久化
    """

    name = "node_import_milvus"

    def process(self, state: ImportGraphState):
        chunks=state.get('chunks','')
        if not chunks:
            raise ValueError('没有chunks文件')
        # 向量化节点(node_bge_embedding)必须先执行，否则 dense_vector/sparse_vector 不存在
        if chunks[0].get("dense_vector") is None or chunks[0].get("sparse_vector") is None:
            raise ValueError(
                'chunks 中缺少 dense_vector / sparse_vector，请先运行 node_bge_embedding 节点生成向量'
            )
        dim = len(chunks[0].get("dense_vector"))
        file_title = state.get("file_title", "")

        milvus_client=get_milvus_client()
        collection_name=MilvusConfig.chunks_collection

        # 并发安全建表：串行化“检查+建表+等索引”，防止多任务同时建表/索引未就绪
        required_indexes = ("dense_vector_index", "sparse_vector_index")
        with _chunks_collection_lock:
            if not milvus_client.has_collection(collection_name):
                logger.info('表不存在，正在创建表')
                schema=milvus_client.create_schema(
                    auto_id=True
                )
                schema.add_field(
                    field_name="id",
                    datatype=DataType.INT64,
                    is_primary=True,
                    auto_id=True
                )
                schema.add_field(
                    field_name="item_name",
                    datatype=DataType.VARCHAR,
                    max_length=256
                )
                schema.add_field(
                    field_name="book_name",
                    datatype=DataType.VARCHAR,
                    max_length=256
                )
                schema.add_field(
                    field_name="file_title",
                    datatype=DataType.VARCHAR,
                    max_length=256
                )
                schema.add_field(
                    field_name="content",
                    datatype=DataType.VARCHAR,
                    max_length=4096
                )
                schema.add_field(
                    field_name="title",
                    datatype=DataType.VARCHAR,
                    max_length=512
                )
                schema.add_field(
                    field_name="part",
                    datatype=DataType.INT64
                )
                # 需求 §5 元数据字段（听书知识库：作者/条目/类别/内容类型/时长）
                schema.add_field(
                    field_name="author",
                    datatype=DataType.VARCHAR,
                    max_length=256
                )
                schema.add_field(
                    field_name="entry_name",
                    datatype=DataType.VARCHAR,
                    max_length=256
                )
                schema.add_field(
                    field_name="category",
                    datatype=DataType.VARCHAR,
                    max_length=512
                )
                schema.add_field(
                    field_name="content_type",
                    datatype=DataType.VARCHAR,
                    max_length=64
                )
                schema.add_field(
                    field_name="duration",
                    datatype=DataType.VARCHAR,
                    max_length=64
                )
                schema.add_field(
                    field_name="dense_vector",
                    datatype=DataType.FLOAT_VECTOR,
                    dim=dim
                )
                schema.add_field(
                    field_name="sparse_vector",
                    datatype=DataType.SPARSE_FLOAT_VECTOR,
                )

                index_params=milvus_client.prepare_index_params()
                index_params.add_index(
                    field_name="dense_vector",
                    index_type="IVF_FLAT",  # AUTOINDEX
                    index_name="dense_vector_index",
                    metric_type="COSINE",
                    params={"nlist": 128, "nprobe": 10}
                )
                index_params.add_index(
                    field_name="sparse_vector",
                    index_type="SPARSE_INVERTED_INDEX",
                    index_name="sparse_vector_index",
                    metric_type="IP",
                    params={
                        "inverted_index_algo": "DAAT_MAXSCORE",
                        # 高效的稀疏检索算法
                        "normalize": True,
                        # ↑ L2 归一化，让内积 (IP) 等价于余弦相似度
                        "quantization": "none"
                        # ↑ 关闭量化，保持原始精度：模型生成的向量已经压缩的一半的精度了（BGE_FP16=1），这里就不再压缩了
                        # "quantization": "none" → 存储原始向量，不压缩
                        # "quantization": "sq8" → 存储压缩后的向量（8-bit 量化
                    }
                )

                milvus_client.create_collection(
                    collection_name=collection_name,
                    schema=schema,
                    index_params=index_params,
                )
                # 索引构建是异步的，必须在锁内等到 Finished，保证后续线程 load 一定成功
                wait_indexes_ready(milvus_client, collection_name, required_indexes)
                logger.info('表创建成功')
            else:
                # 集合已存在：兜底检查索引，缺失则补建（防止历史半成品集合导致 load 报错）
                existing_indexes = set(milvus_client.list_indexes(collection_name) or [])
                missing = [name for name in required_indexes if name not in existing_indexes]
                if missing:
                    logger.warning(f'集合 {collection_name} 缺少索引 {missing}，正在补建')
                    index_params = milvus_client.prepare_index_params()
                    index_params.add_index(
                        field_name="dense_vector",
                        index_type="IVF_FLAT",  # AUTOINDEX
                        index_name="dense_vector_index",
                        metric_type="COSINE",
                        params={"nlist": 128, "nprobe": 10}
                    )
                    index_params.add_index(
                        field_name="sparse_vector",
                        index_type="SPARSE_INVERTED_INDEX",
                        index_name="sparse_vector_index",
                        metric_type="IP",
                        params={
                            "inverted_index_algo": "DAAT_MAXSCORE",
                            # 高效的稀疏检索算法
                            "normalize": True,
                            # ↑ L2 归一化，让内积 (IP) 等价于余弦相似度
                            "quantization": "none"
                        }
                    )
                    milvus_client.create_index(collection_name, index_params)
                    wait_indexes_ready(milvus_client, collection_name, missing)

        milvus_client.load_collection(collection_name=collection_name)
        file_title = file_title.replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"')
        filter_str = f"file_title == '{file_title}'"
        milvus_client.delete(collection_name=collection_name, filter=filter_str)
        # 兜底：旧 chunks 文件可能缺元数据字段，补齐默认值防止 Milvus 插入报错
        for chunk in chunks:
            chunk.setdefault("book_name", "")
            chunk.setdefault("author", "")
            chunk.setdefault("entry_name", "")
            chunk.setdefault("category", "")
            chunk.setdefault("content_type", "")
            chunk.setdefault("duration", "")
        result = milvus_client.insert(collection_name=collection_name, data=chunks)
        ids = result.get("ids")
        for chunk in chunks:
            chunk["id"] = ids.pop(0)
        # 输出目录 = local_dir / file_title，与上游节点的输出目录保持一致
        out_dir = Path(state.get("local_dir", "")) / state.get("file_title", "")
        out_dir.mkdir(parents=True, exist_ok=True)
        with open(out_dir / "chunks_id.json", 'w', encoding='utf-8') as f:
            json.dump(chunks, f, ensure_ascii=False, indent=4)

        # LangGraph 节点必须返回 dict 来更新 state，不能直接返回 list
        return {"chunks": chunks}

if __name__ == '__main__':
    node = NodeImportMilvus()
    with open(r"D:\code\uv1\data\hak180产品安全手册\chunks_item.json", 'r', encoding='utf-8') as f:
        chunks=json.load(f)
    state={
        'chunks':chunks
    }
    res=node(state)
    logger.info(json_tool(res))
