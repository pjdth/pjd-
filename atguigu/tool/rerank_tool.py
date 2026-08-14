import dashscope
from http import HTTPStatus
import json

from atguigu.config.config import RerankConfig
from atguigu.tool.logger import logger

# 以下为华北2（北京）地域的配置，调用时请将{WorkspaceId}替换为真实的业务空间ID，各地域的配置不同。
dashscope.base_http_api_url = RerankConfig.rerank_base_url
dashscope.api_key = RerankConfig.rerank_api_key
def rerank(query,texts,limit=10):
    try:
        resp = dashscope.TextReRank.call(
            model="qwen3-vl-rerank",
            query=query,
            documents=texts,
            top_n=limit,
            return_documents=True,
            instruct="Given a web search query, retrieve relevant passages that answer the query."
        )

        if resp.status_code == HTTPStatus.OK:
            # print(resp)
            # print(json.dumps(resp, default=str, ensure_ascii=False, indent=4))
            return [{"index": item.index, "score": item.relevance_score} for item in resp.output['results']]
        else:
            raise Exception("重排序出现问题")
    except Exception as e:
        logger.error(f"Error: {e}")
        raise e

if __name__ == '__main__':
    query='你是？'
    tests=['我是红神','我是红p','我是区']
    rerank(query,tests)