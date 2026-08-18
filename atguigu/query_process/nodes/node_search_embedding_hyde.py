# atguigu/query_process/nodes/node_search_embedding_hyde.py
import json

from langchain.chat_models import init_chat_model

from atguigu.config.config import LLMConfig, MilvusConfig
from atguigu.config.prompt import HYDE_PROMPT
from atguigu.query_process.base import NodeBase
from atguigu.query_process.state import QueryGraphState
from atguigu.tool.bgem3_client_tool import get_bge_m3_embedding
from atguigu.tool.json_tool import json_tool
from atguigu.tool.logger import logger
from atguigu.tool.milvus_client_tool import create_reqs, search_hybrid


class NodeSearchEmbeddingHyde(NodeBase):
    """
    节点功能：HyDE (Hypothetical Document Embedding)
    先让 LLM 生成假设性答案，再对答案进行向量检索，提高召回率。
    """

    # 覆盖基类的 name 属性，标识节点名称
    name: str = "node_search_embedding_hyde"

    def process(self, state: QueryGraphState):
        """
        节点逻辑
        :param state: 工作流状态对象
        :return: 更新后的状态对象
        """
        rewritten_query = state.get("rewritten_query")
        item_names = state.get("item_names")
        if not rewritten_query:
            logger.error("rewritten_query is None")
            raise ValueError("rewritten_query is None")
        if not item_names:
            logger.error("item_names is None")
            raise ValueError("item_names is None")

        llm=init_chat_model(
            model=LLMConfig.llm_default_model,
            model_provider="openai",
            temperature=LLMConfig.llm_default_temperature,
            base_url=LLMConfig.openai_api_base,
            api_key=LLMConfig.openai_api_key
        )
        messages = [
            {"role": "user", "content":HYDE_PROMPT.format(rewritten_query=rewritten_query)}
        ]
        res=llm.invoke(messages)
        print(res.content)
        merge_query=rewritten_query+res.content
        embeddings=get_bge_m3_embedding([merge_query])
        logger.info(embeddings)
        dense_data=embeddings.get("dense")[0]
        sparse_data=embeddings.get("sparse")[0]
        print(dense_data, sparse_data)
        item_names = [
            item_name.replace("\\", "\\\\").replace('"', '\\"').replace("'", "\\'")
            for item_name in item_names
        ]

        reqs=create_reqs(
            dense_data=dense_data,
            sparse_data=sparse_data,
            dense_anns_field="dense_vector",
            sparse_anns_field="sparse_vector",
            expr=f'item_name in {json.dumps(item_names)}',
            limit=10,
        )
        logger.info(reqs)
        res=search_hybrid(
            reqs=reqs,
            collection_name=MilvusConfig.chunks_collection,
            limit=10,
            ranker=(0.8, 0.2),
            output_fields=["id", "file_title", "title", "content", "item_name"],
        )
        print(res)
        return {
            "hyde_embedding_chunks": [
                {
                    **r.get("entity"),
                    "score": r.get("distance"),
                    'source':'local'
                }
                for r in res[0]
            ]
        }
if __name__ == "__main__":
    init_state = {
        "rewritten_query": "关于HAK180烫金机如何使用",
        "item_names": ["HAK180烫金机"]
    }
    node_search_embedding_hyde = NodeSearchEmbeddingHyde()
    result = node_search_embedding_hyde(init_state)
    logger.info(json_tool(result))