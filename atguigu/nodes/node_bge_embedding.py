import json

from atguigu.import_process.base import NodeBase
from atguigu.import_process.state import ImportGraphState
from atguigu.tool.bgem3_client_tool import get_bge_m3_embedding
from atguigu.tool.json_tool import json_tool


class NodeBGEEmbedding(NodeBase):
    """
    混合向量化节点：使用 BGE-M3 模型将文本转换为向量
    """

    name = "node_bge_embedding"

    def process(self, state: ImportGraphState):
        chunks=state.get('chunks','')
        if not chunks:
            raise ValueError('没有chunks文件')

        for i in range(0,len(chunks),3):
            chunk_list=chunks[i:i+3]
            chunk_k_content_list=[f'{}{}' for chunk in chunk_list ]
            embedding= get_bge_m3_embedding(chunk_k_content_list)
            for idx,chunk in enumerate(chunk_list):

        return state

if __name__=='__main__':
    node=NodeBGEEmbedding()
    with open() as f:
        chunks=json.load(f)
    state={
        'chunks':chunks
    }
    res=node(state)
    logger.info(json_tool(res))