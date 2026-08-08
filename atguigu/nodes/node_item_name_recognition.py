import json

from langchain.chat_models import init_chat_model
from openai import api_key

from atguigu.config.config import LLMConfig, MilvusConfig
from atguigu.import_process.base import NodeBase
from atguigu.import_process.state import ImportGraphState
from atguigu.tool.bgem3_client_tool import get_bge_m3_embedding
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
        print(chunks_k_list)
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

        messages=[]

        res=llm.invoke(messages)

        # print(res.content)

        res_content=res.content
        res_content = res_content.replace(" ", "").replace("\n", "").replace("\t", "")

        milvus_client=get_milvus_client()
        if not milvus_client:
            logger.error('milvus_client不存在')
            raise Exception('milvus_client不存在')

        collection_name=MilvusConfig.item_name_collection
        #建立表
        #建立表属性
        #建立表索引

        #抽入数据前判断里面有没有重复的
        #插入
        embeding=get_bge_m3_embedding([])

        data={
            'item_name':1,
            'file_title':1,
            'dense_vector':1,
            'sparse_vector':1,
        }
        res=milvus_client.insert(
            collection_name=collection_name,
            data=data
        )

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