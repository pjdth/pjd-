import json
import threading
from pathlib import Path

from langchain.chat_models import init_chat_model
from pymilvus import DataType

from atguigu.config.config import LLMConfig, MilvusConfig
from atguigu.config.prompt import ITEM_NAME_SYSTEM_PROMPT, ITEM_NAME_USER_PROMPT_TEMPLATE
from atguigu.import_process.base import NodeBase
from atguigu.import_process.state import ImportGraphState
from atguigu.tool.bgem3_client_tool import get_bge_m3_embedding
from atguigu.tool.json_tool import json_tool
from atguigu.tool.logger import logger
from atguigu.tool.milvus_client_tool import milvus_client, get_milvus_client, wait_indexes_ready

# 全局建表锁：多个上传任务并发执行时，串行化 item_name 集合的“检查+建表+等索引”流程，
# 避免重复建表或索引未就绪就 load 报错（no vector index on field: sparse_vector）
_collection_lock = threading.Lock()


class NodeItemNameRecognition(NodeBase):
    """
    主体识别节点：主体识别与标签提取
    """

    name = "node_item_name_recognition"

    def get_chunks(self, state):
        chunks = state.get("chunks")
        # print(chunks)
        file_title = state.get("file_title")
        if not chunks:
            raise Exception("chunks为空，必须有值才能进行主体识别")
        if not file_title:
            raise Exception("file_title为空，必须有值才能进行主体识别")
        chunks_k_list = chunks[:10]
        # print(chunks_k_list)
        max_len = 10000
        content_str = '\n'
        for idx, chunk in enumerate(chunks_k_list, start=1):
            file_title = chunk.get('file_title')
            title = chunk.get("title")
            content = chunk.get("content")
            chunk_str = f"切片为{idx}文件名为{file_title}这一段标题是{title}内容是{content}"
            content_str += chunk_str
            if len(content_str) > max_len:
                logger.info('内容已达最大内容')
                break
        # print(content_str)
        content_str = content_str[:max_len]
        return chunks, content_str, file_title

    def get_llm_res(self, content_str, file_title):
        llm = init_chat_model(
            model=LLMConfig.item_model,
            model_provider='openai',
            api_key=LLMConfig.openai_api_key,
            base_url=LLMConfig.openai_api_base,

        )
        # ITEM_NAME_SYSTEM_PROMPT 已从 atguigu.config.prompt 导入，统一在 prompt.py 维护

        messages = [
            {"role": "system", "content": ITEM_NAME_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": ITEM_NAME_USER_PROMPT_TEMPLATE.format(file_title=file_title, context=content_str)
            }
        ]
        res = llm.invoke(messages)
        res_content = res.content
        res_content = res_content.replace(" ", "").replace("\n", "").replace("\t", "")
        # 兜底：模型若返回空串（或清理后变空），统一记为“未识别内容”，避免空 item_name 写入 Milvus 导致报错
        if not res_content:
            res_content = "未识别内容"
        print('______________主体识别出的内容为________________',res_content)
        return res_content

    def _build_schema(self, milvus_client):
        """构建 item_name 集合的 schema（含 dense/sparse 向量字段）"""
        schema = milvus_client.create_schema(auto_id=True)
        schema.add_field(
            field_name="id",
            datatype=DataType.INT64,
            is_primary=True,
            is_unique=True,
        ).add_field(
            field_name="item_name",
            datatype=DataType.VARCHAR,
            max_length=500,
            description="item name of the item"
        ).add_field(
            field_name="file_title",
            datatype=DataType.VARCHAR,
            max_length=500,
            description="file title of the item"
        ).add_field(
            field_name="dense_vector",
            datatype=DataType.FLOAT_VECTOR,
            dim=1024,
            description="dense vector of the item"
        ).add_field(
            field_name="sparse_vector",
            datatype=DataType.SPARSE_FLOAT_VECTOR,
            description="sparse vector of the item"
        )
        return schema

    def _build_index_params(self, milvus_client):
        """构建 item_name 集合的索引参数（dense + sparse）"""
        index_params = milvus_client.prepare_index_params()
        index_params.add_index(
            field_name="dense_vector",
            index_name="dense_vector_index",
            index_type="IVF_FLAT",
            metric_type="COSINE",
            params={"nlist": 128, "nprobe": 10},
        )
        index_params.add_index(
            field_name="sparse_vector",
            index_name="sparse_vector_index",
            index_type="SPARSE_INVERTED_INDEX",
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
        return index_params

    def _ensure_collection_ready(self, milvus_client, collection_name):
        """保证集合存在且索引就绪。多任务并发上传时用全局锁串行化“检查+建表+等索引”，
        避免多个线程同时建同一个表、或索引未就绪就 load 报错。"""
        required_indexes = ("dense_vector_index", "sparse_vector_index")
        with _collection_lock:
            if not milvus_client.has_collection(collection_name):
                logger.info('表不存在，正在创建表')
                schema = self._build_schema(milvus_client)
                index_params = self._build_index_params(milvus_client)
                milvus_client.create_collection(
                    collection_name=collection_name,
                    schema=schema,
                    index_params=index_params,
                )
                # 索引构建是异步的，必须在锁内等到 Finished，保证后续线程 load 一定成功
                wait_indexes_ready(milvus_client, collection_name, required_indexes)
            else:
                # 集合已存在：兜底检查索引，缺失则补建（防止历史半成品集合导致 load 报错）
                existing_indexes = set(milvus_client.list_indexes(collection_name) or [])
                missing = [name for name in required_indexes if name not in existing_indexes]
                if missing:
                    logger.warning(f'集合 {collection_name} 缺少索引 {missing}，正在补建')
                    index_params = self._build_index_params(milvus_client)
                    milvus_client.create_index(collection_name, index_params)
                    wait_indexes_ready(milvus_client, collection_name, missing)

    def save_state(self, state, res_content, file_title, chunks):
        milvus_client = get_milvus_client()
        if not milvus_client:
            logger.error('milvus_client不存在')
            raise Exception('milvus_client不存在')

        collection_name = MilvusConfig.item_name_collection
        # 并发安全建表：串行化“检查+建表+等索引”，防止多任务同时建表/索引未就绪
        self._ensure_collection_ready(milvus_client, collection_name)
        milvus_client.load_collection(collection_name)
        item_name = res_content.replace("\\", "\\\\").replace("\'", "\\'").replace('\"', '\\"')
        milvus_client.delete(collection_name=collection_name, filter=f"item_name=='{item_name}'")
        # 插入
        embedding = get_bge_m3_embedding([item_name])

        data = {
            "file_title": file_title,
            "item_name": item_name,
            "dense_vector": embedding["dense"][0],
            "sparse_vector": embedding["sparse"][0]
        }
        res = milvus_client.insert(
            collection_name=collection_name,
            data=data
        )

        for chunk in chunks:
            chunk["item_name"] = item_name
        # print(chunks)

        # 写入硬盘chunks
        # 输出目录 = local_dir / file_title，与 node_pdf_to_md 的解压目录保持一致
        out_dir = Path(state.get("local_dir", "")) / state.get("file_title", "")
        out_dir.mkdir(parents=True, exist_ok=True)
        with open(out_dir / "chunks_item.json", "w", encoding="utf-8") as f:
            f.write(json_tool(chunks))

        # print(res)
        return state

    def process(self, state: ImportGraphState):
        # 拿取前1w的chunks用于主体识别
        chunks, content_str, file_title = self.get_chunks(state)
        #调用大模型进行主体识别
        res_content = self.get_llm_res(content_str, file_title)
        #拿到主体识别结果后，先进行向量化，再存入Milvus
        state=self.save_state(state, res_content, file_title, chunks)

        return state







if __name__ == '__main__':
    node=NodeItemNameRecognition()
    with open(r"D:\code\uv1\data\hak180产品安全手册\chunks.json", "r", encoding="utf-8") as f:
        chunks_json=f.read()

    state={
        "chunks":json.loads(chunks_json),
        'file_title':'hak180产品安全手册'
    }
    node.process(state)