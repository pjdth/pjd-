# atguigu/query_process/nodes/node_recommend.py
from langchain.chat_models import init_chat_model

from atguigu.config.config import LLMConfig, MilvusConfig
from atguigu.config.prompt import RECOMMEND_PROMPT
from atguigu.query_process.base import NodeBase
from atguigu.query_process.state import QueryGraphState
from atguigu.tool.bgem3_client_tool import get_bge_m3_embedding
from atguigu.tool.logger import logger
from atguigu.tool.milvus_client_tool import create_reqs, search_hybrid, collection_exists
from atguigu.tool.mongo_client_tool import add_or_update_history
from atguigu.tool.task_utils import put_data


class NodeRecommend(NodeBase):
    """
    书籍推荐模式：对用户需求做混合检索，按书名聚合文档，
    生成结构化推荐（书籍列表 + 特色 + 适合人群 + 推荐理由）。
    """

    name: str = "node_recommend"

    def get_recommend_docs(self, query):
        """对 query 做混合检索，按书名聚合并限制数量"""
        embeddings = get_bge_m3_embedding([query])
        reqs = create_reqs(
            dense_data=embeddings["dense"][0],
            sparse_data=embeddings["sparse"][0],
            dense_anns_field="dense_vector",
            sparse_anns_field="sparse_vector",
            limit=20,
        )
        res = search_hybrid(
            collection_name=MilvusConfig.chunks_collection,
            reqs=reqs,
            ranker=(0.8, 0.2),
            limit=20,
            output_fields=["id", "file_title", "title", "content", "item_name",
                           "author", "category", "content_type", "entry_name", "duration"],
        )
        docs = [
            {
                **item.get("entity"),
                "score": item.get("distance"),
                "source": "local",
            }
            for item in res[0]
        ]
        # 按书名聚合：每本书保留分数最高的 2 个切片，最多保留 5 本书
        book_groups = {}
        for doc in docs:
            book = doc.get("item_name") or doc.get("file_title") or "未知书籍"
            book_groups.setdefault(book, []).append(doc)
        merged = []
        for book_docs in book_groups.values():
            book_docs.sort(key=lambda x: x.get("score") or 0, reverse=True)
            merged.extend(book_docs[:2])
        merged.sort(key=lambda x: x.get("score") or 0, reverse=True)
        return merged[:10]

    def process(self, state: QueryGraphState):
        query = state.get("original_query") or state.get("rewritten_query") or ""
        task_id = state.get("task_id", "")
        session_id = state.get("session_id", "")

        # 优雅降级：知识库集合未创建（还没导入内容）时给友好提示，不抛异常
        if not collection_exists(MilvusConfig.chunks_collection):
            answer = "知识库还没有书籍资料，请先通过导入服务上传书籍内容（PDF/MD），再来让我为你推荐。"
            if task_id:
                put_data(task_id, "final", {"answer": answer})
            return {"answer": answer, "reranked_docs": [], "intent": "recommend"}

        docs = self.get_recommend_docs(query)

        # 组装带元数据的上下文
        context = ""
        for idx, doc in enumerate(docs, start=1):
            context += (
                f"[{idx}]《{doc.get('item_name', '')}》"
                f"作者:{doc.get('author', '')} 类别:{doc.get('category', '')} "
                f"时长:{doc.get('duration', '')} 类型:{doc.get('content_type', '')}\n"
                f"{doc.get('content', '')}\n\n"
            )

        prompt = RECOMMEND_PROMPT.format(query=query, context=context)
        llm = init_chat_model(
            model=LLMConfig.item_model,
            model_provider="openai",
            api_key=LLMConfig.openai_api_key,
            base_url=LLMConfig.openai_api_base,
            temperature=LLMConfig.llm_default_temperature,
        )
        answer = ""
        for msg in llm.stream([{"role": "user", "content": prompt}]):
            put_data(task_id, "delta", {"delta": msg.content})
            answer += msg.content

        # 落历史
        if answer and session_id:
            add_or_update_history(session_id, "assistant", answer)

        logger.info(f"推荐模式完成，命中 {len(docs)} 个切片")
        return {
            "answer": answer,
            "reranked_docs": docs,
            "intent": "recommend",
        }
