# atguigu/query_process/nodes/node_detail.py
import re

from langchain.chat_models import init_chat_model

from atguigu.config.config import LLMConfig, MilvusConfig
from atguigu.config.prompt import DETAIL_PROMPT
from atguigu.query_process.base import NodeBase
from atguigu.query_process.state import QueryGraphState
from atguigu.tool.bgem3_client_tool import get_bge_m3_embedding
from atguigu.tool.logger import logger
from atguigu.tool.milvus_client_tool import create_reqs, search_hybrid, collection_exists
from atguigu.tool.mongo_client_tool import add_or_update_history
from atguigu.tool.task_utils import put_data


class NodeDetail(NodeBase):
    """
    书籍详情模式：检索用户所指书籍的全部内容切片（按内容类型组织），
    生成结构化详情（简介/作者/时长/标签/亮点/常见问答）。
    """

    name: str = "node_detail"

    def get_book_name_from_query(self, query):
        """优先从书名号《》抽取书名"""
        m = re.search(r'《(.+?)》', query)
        return m.group(1) if m else ""

    def get_detail_docs(self, query):
        """混合检索 chunks，按书名聚合后返回主书的最多 15 个切片（覆盖各内容类型）"""
        embeddings = get_bge_m3_embedding([query])
        reqs = create_reqs(
            dense_data=embeddings["dense"][0],
            sparse_data=embeddings["sparse"][0],
            dense_anns_field="dense_vector",
            sparse_anns_field="sparse_vector",
            limit=30,
        )
        res = search_hybrid(
            collection_name=MilvusConfig.chunks_collection,
            reqs=reqs,
            ranker=(0.8, 0.2),
            limit=30,
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
        # 按书名聚合，取总得分最高的书作为详情目标
        book_groups = {}
        for doc in docs:
            book = doc.get("item_name") or doc.get("file_title") or "未知书籍"
            book_groups.setdefault(book, []).append(doc)
        if not book_groups:
            return [], ""
        best_book = max(
            book_groups,
            key=lambda b: sum(d.get("score") or 0 for d in book_groups[b]),
        )
        book_docs = sorted(
            book_groups[best_book],
            key=lambda x: x.get("score") or 0,
            reverse=True,
        )
        return book_docs[:15], best_book

    def process(self, state: QueryGraphState):
        query = state.get("original_query") or state.get("rewritten_query") or ""
        task_id = state.get("task_id", "")
        session_id = state.get("session_id", "")

        # 优雅降级：知识库集合未创建（还没导入内容）时给友好提示，不抛异常
        if not collection_exists(MilvusConfig.chunks_collection):
            answer = "知识库还没有书籍资料，请先通过导入服务上传书籍内容（PDF/MD），再来查询书籍详情。"
            if task_id:
                put_data(task_id, "final", {"answer": answer})
            return {"answer": answer, "reranked_docs": [], "intent": "detail"}

        docs, book_name = self.get_detail_docs(query)
        if not docs:
            answer = "抱歉，知识库中暂未找到该书的相关资料，请确认书名后重试。"
            if task_id:
                put_data(task_id, "final", {"answer": answer})
            return {"answer": answer, "reranked_docs": [], "intent": "detail"}

        # 组装按内容类型组织的上下文
        context = ""
        for idx, doc in enumerate(docs, start=1):
            context += (
                f"[{idx}][类型:{doc.get('content_type', '')}]"
                f"[作者:{doc.get('author', '')}][类别:{doc.get('category', '')}]"
                f"[时长:{doc.get('duration', '')}]\n{doc.get('content', '')}\n\n"
            )

        prompt = DETAIL_PROMPT.format(book_name=book_name, context=context)
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

        if answer and session_id:
            add_or_update_history(session_id, "assistant", answer)

        logger.info(f"详情模式完成，书籍: {book_name}，切片: {len(docs)} 个")
        return {
            "answer": answer,
            "reranked_docs": docs,
            "intent": "detail",
        }
