import json

from langchain.chat_models import init_chat_model
from pymilvus import DataType

from atguigu.config.config import LLMConfig, MilvusConfig
from atguigu.import_process.base import NodeBase
from atguigu.import_process.state import ImportGraphState
from atguigu.tool.bgem3_client_tool import get_bge_m3_embedding
from atguigu.tool.json_tool import json_tool
from atguigu.tool.logger import logger
from atguigu.tool.milvus_client_tool import milvus_client, get_milvus_client


class NodeItemNameRecognition(NodeBase):
    """
    主体识别节点：主体识别与标签提取
    """

    name = "node_item_name_recognition"

    def process(self, state: ImportGraphState):
        chunks=state.get("chunks_json")
        # print(chunks)
        file_title=state.get("file_title")
        if not chunks:
            raise Exception("chunks为空，必须有值才能进行主体识别")

        if not file_title:
            raise Exception("file_title为空，必须有值才能进行主体识别")

        chunks_k_list=chunks[:10]
        # print(chunks_k_list)
        max_len=10000
        content_str='\n'
        for idx,chunk in enumerate(chunks_k_list,start=1):
            file_title=chunk.get('file_title')
            title=chunk.get("title")
            content=chunk.get("content")
            chunk_str=f"切片为{idx}文件名为{file_title}这一段标题是{title}内容是{content}"
            content_str += chunk_str
            if len(content_str)>max_len:
                logger.info('内容已达最大内容')
                break
        # print(content_str)
        content_str=content_str[:max_len]

        llm=init_chat_model(
            model=LLMConfig.item_model,
            model_provider='openai',
            api_key=LLMConfig.openai_api_key,
            base_url=LLMConfig.openai_api_base,

        )

        ITEM_NAME_SYSTEM_PROMPT = "你是一个专业的商品名称识别模型，请根据提供的信息，识别商品名称。"

        # User Prompt Template
        ITEM_NAME_USER_PROMPT_TEMPLATE = """
                        请从以下信息中识别出商品名称与型号：
                        文件名：{file_title}

                        正文切片（用于辅助识别）：
                        {context}

                        要求：
                        1. 返回内容为字符串形式，最好是带品牌、型号和名称的完整商品名称。比如：苏伯尓5000W大功率电磁炉；
                        2. 返回结果应该只包含商品名称，不要添加任何解释或其他内容；
                        3. 如果无法识别商品名称,请返回空字符串。
                        """
        messages=[
            {"role": "system", "content": ITEM_NAME_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": ITEM_NAME_USER_PROMPT_TEMPLATE.format(file_title=file_title, context=content_str)
            }
        ]

        res=llm.invoke(messages)

        res_content=res.content
        res_content = res_content.replace(" ", "").replace("\n", "").replace("\t", "")
        print(res_content)

        milvus_client=get_milvus_client()
        if not milvus_client:
            logger.error('milvus_client不存在')
            raise Exception('milvus_client不存在')

        collection_name=MilvusConfig.item_name_collection
        #建立表前先判断有没有表
        if not milvus_client.has_collection(collection_name):
            logger.info('表不存在，正在创建表')
            # 建立表属性
            schema=milvus_client.create_schema(
                auto_id=True,
            )

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

            #建立表索引
            index_params=milvus_client.prepare_index_params()
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
            milvus_client.create_collection(
                collection_name=collection_name,
                schema=schema,
                index_params=index_params,
            )
        #抽入数据前判断里面有没有重复的
        milvus_client.load_collection(collection_name)
        item_name = res_content.replace("\\", "\\\\").replace("\'", "\\'").replace('\"', '\\"')
        milvus_client.delete(collection_name=collection_name, filter=f"item_name=='{item_name}'")
        #插入
        embedding=get_bge_m3_embedding([item_name])

        data={
            "file_title": file_title,
            "item_name": item_name,
            "dense_vector": embedding["dense"][0],
            "sparse_vector": embedding["sparse"][0]
        }
        res=milvus_client.insert(
            collection_name=collection_name,
            data=data
        )

        for chunk in chunks:
            chunk["item_name"] = item_name

        #print(chunks)
        #写入硬盘chunks
        with open(r"D:\code\uv1\data\out\hak180产品安全手册\chunks_item.json", "w", encoding="utf-8") as f:
            f.write(json_tool(chunks))

        print(res)
        return state

if __name__ == '__main__':
    node=NodeItemNameRecognition()
    with open(r"D:\code\uv1\data\out\hak180产品安全手册\chunks.json", "r", encoding="utf-8") as f:
        chunks_json=f.read()

    state={
        "chunks_json":json.loads(chunks_json),
        'file_title':'hak180产品安全手册'
    }
    node.process(state)