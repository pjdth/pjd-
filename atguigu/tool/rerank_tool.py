import dashscope
from http import HTTPStatus
import json

from atguigu.config.config import RerankConfig
from atguigu.config.prompt import RERANK_INSTRUCT
from atguigu.tool.logger import logger

# 以下为华北2（北京）地域的配置，调用时请将{WorkspaceId}替换为真实的业务空间ID，各地域的配置不同。
dashscope.base_http_api_url = RerankConfig.rerank_base_url
dashscope.api_key = RerankConfig.rerank_api_key
def rerank(query,texts,limit=10):
    # 入参校验：qwen3-vl-rerank 不接受空文档，提前拦截并给出明确报错
    if not query or not query.strip():
        raise ValueError("rerank 入参 query 为空，无法重排序")
    valid_texts = [t for t in (texts or []) if t and str(t).strip()]
    if not valid_texts:
        raise ValueError("rerank 入参 texts 为空或全为空内容，无法重排序")
    if len(valid_texts) != len(texts):
        # 调用方应在上游过滤，这里只兜底：丢弃空内容后索引会错位，直接报错提示
        raise ValueError("rerank 入参 texts 中存在空内容，请先在上游过滤后再调用")
    try:
        resp = dashscope.TextReRank.call(
            model="qwen3-vl-rerank",
            query=query,
            documents=texts,
            top_n=limit,
            return_documents=True,
            instruct=RERANK_INSTRUCT
        )

        if resp.status_code == HTTPStatus.OK:
            # print(resp)
            # print(json.dumps(resp, default=str, ensure_ascii=False, indent=4))
            return [{"index": item.index, "score": item.relevance_score} for item in resp.output['results']]
        else:
            raise Exception(f"重排序出现问题，HTTP状态码:{resp.status_code}")
    except Exception as e:
        logger.error(f"Error: {e}")
        raise e

if __name__ == '__main__':
    query='你是？'
    tests=['我是红神','我是红p','我是区']
    rerank(query,tests)