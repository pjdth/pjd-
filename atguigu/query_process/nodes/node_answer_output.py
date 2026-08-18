# atguigu/query_process/nodes/node_answer_output.py
import re

from langchain.chat_models import init_chat_model

from atguigu.config.config import LLMConfig
from atguigu.config.prompt import ANSWER_PROMPT
from atguigu.query_process.base import NodeBase
from atguigu.query_process.state import QueryGraphState
from atguigu.tool.logger import logger
from atguigu.tool.mongo_client_tool import add_or_update_history
from atguigu.tool.task_utils import put_data


class NodeAnswerOutput(NodeBase):
    """
    节点功能: 答案生成
    """

    # 覆盖基类的 name 属性，标识节点名称
    name: str = "node_answer_output"
    def get_prompt(self, state: QueryGraphState,):
        pass

    def process(self, state: QueryGraphState):
        answer=state.get("answer", "")
        task_id=state.get("task_id", "")

        if answer:
            put_data(task_id,"final", {"answer": answer})
        else:
            # 把 chunks 合并成一个字符串，方便后续生成答案
            chunks=state.get("reranked_docs")
            chunk_content = ""
            for idx, chunk in enumerate(chunks, start=1):
                title = chunk.get("title")
                content = chunk.get("content")
                source = chunk.get("source")
                url = chunk.get("url")
                score = chunk.get("score")
                content = f"[{idx}][{source}][{score}][{title}][{url}]\n{content}\n\n"
                chunk_content += content
            #拿到history,也作为输入
            history = state.get("history")
            history_content = ""
            for h in history:
                role = h.get("role")
                text = h.get("text")
                h_content = f"[{role}]: {text}\n\n"
                history_content += h_content

             #提示词整理
            item_names = state.get("item_names")
            item_name_str = ",".join(item_names)
            query = state.get("rewritten_query")
            prompt = ANSWER_PROMPT.format(
                context=chunk_content,
                history=history_content,
                item_names=item_name_str,
                question=query,
            )
            if len(prompt) >= 12000:
                prompt = prompt[:12000]


            messages = [
                {"role": "user", "content": prompt}
            ]
            llm = init_chat_model(
                model=LLMConfig.item_model,
                model_provider="openai"
            )
            answer = ""
            res = llm.stream(messages)
            for msg in res:
                put_data(task_id, "delta", {"delta": msg.content})
                answer += msg.content

            images = []
            seen = set()  # 用于去重，避免同一张图片重复出现
            md_img_pattern = re.compile(r'!\[.*?\]\((.*?)\)')
            for i, doc in enumerate(chunks):
                # 检查 text 字段中的 Markdown 图片 (主要针对 Local Chunk)
                text = doc.get("content")
                matches = md_img_pattern.findall(text)
                for img_url in matches:
                    img_url = img_url.strip()
                    if img_url and img_url not in seen:
                        seen.add(img_url)
                        images.append(img_url)
            if answer:
                add_or_update_history(
                    session_id=state.get("session_id"),
                    role="assistant",
                    text=answer,
                    image_urls=images,
                    rewritten_query=query,
                    item_names=item_names,
                )
                # 把完整 answer 一并放进 final，避免只靠前端 delta 拼接兜底（与分支 A 保持一致）
                put_data(task_id, "final", {"answer": answer, "image_urls": images})
        return {
            "answer": answer,
        }


        return state