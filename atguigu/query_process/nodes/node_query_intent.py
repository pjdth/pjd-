# atguigu/query_process/nodes/node_query_intent.py
import re

from langchain.chat_models import init_chat_model

from atguigu.config.config import LLMConfig
from atguigu.config.prompt import QUERY_INTENT_PROMPT
from atguigu.query_process.base import NodeBase
from atguigu.query_process.state import QueryGraphState
from atguigu.tool.logger import logger


class NodeQueryIntent(NodeBase):
    """
    意图识别节点：判断用户问题是"书籍推荐 / 书籍详情 / 知识问答"，
    查询图据此分流到不同的检索与回答逻辑。
    """

    name: str = "node_query_intent"

    # 规则优先：命中推荐关键词直接判定 recommend（快、稳、省一次 LLM 调用）
    RECOMMEND_KEYWORDS = [
        "推荐", "有哪些", "什么书", "哪本", "书单", "求推", "想听", "有什么",
        "适合", "通勤", "睡前", "夜深", "碎片", "轻松", "治愈",
    ]
    # 详情关键词：出现书名号且带详情意图词
    DETAIL_KEYWORDS = ["介绍", "讲什么", "讲了什么", "怎么样", "简介", "内容", "作者", "时长", "详情", "看点", "问题", "亮点", "标签"]

    def guess_by_rules(self, query):
        """规则初判。
        书名号指向具体书时：详情词→detail、选书词→recommend，其余交给 LLM；
        无书名号时：推荐词→recommend，其余交给 LLM。
        """
        has_book = re.search(r'《.+?》', query)
        if has_book:
            if any(kw in query for kw in self.DETAIL_KEYWORDS):
                return "detail"
            if any(kw in query for kw in ("推荐", "有哪些", "书单", "求推", "想听", "有什么")):
                return "recommend"
            return ""
        if any(kw in query for kw in self.RECOMMEND_KEYWORDS):
            return "recommend"
        return ""

    def guess_by_llm(self, query):
        """LLM 判断意图；异常时返回 qa 兜底，保证链路不中断"""
        try:
            llm = init_chat_model(
                model=LLMConfig.item_model,
                model_provider="openai",
                api_key=LLMConfig.openai_api_key,
                base_url=LLMConfig.openai_api_base,
                temperature=0,
            )
            res = llm.invoke([
                {"role": "user", "content": QUERY_INTENT_PROMPT.format(query=query)}
            ])
            intent = str(res.content).strip().lower()
            # 兼容模型输出多余内容的情况，只取第一个合法意图词
            for candidate in ("recommend", "detail", "qa"):
                if candidate in intent:
                    return candidate
            return "qa"
        except Exception as e:
            logger.warning(f"意图识别 LLM 调用失败，降级为 qa: {e}")
            return "qa"

    def process(self, state: QueryGraphState):
        query = state.get("original_query", "") or state.get("rewritten_query", "")
        if not query:
            raise ValueError("original_query 为空，无法识别意图")

        intent = self.guess_by_rules(query)
        if not intent:
            intent = self.guess_by_llm(query)
        logger.info(f"意图识别结果: {intent} | query: {query}")
        return {"intent": intent}


if __name__ == "__main__":
    node = NodeQueryIntent()
    for q in [
        "有哪些科幻类有声书？",
        "推荐一本适合通勤听的悬疑小说",
        "《三体》讲了什么？",
        "活着适合什么人听？",
    ]:
        r = node({"original_query": q})
        print(f"{q}  ->  {r['intent']}")
