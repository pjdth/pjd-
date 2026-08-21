import json

from atguigu.import_process.base import NodeBase
from atguigu.import_process.state import ImportGraphState
from atguigu.tool.bgem3_client_tool import get_bge_m3_embedding
from atguigu.tool.json_tool import json_tool
from atguigu.tool.logger import logger


class NodeBGEEmbedding(NodeBase):
    """
    混合向量化节点：使用 BGE-M3 模型将文本转换为向量
    """

    name = "node_bge_embedding"

    def process(self, state: ImportGraphState):
        chunks=state.get('chunks','')
        print("——————————chunks———————————", chunks)
        if not chunks:
            raise ValueError('没有chunks文件')

        for i in range(0,len(chunks),3):
            chunk_list=chunks[i:i+3]
            chunk_k_content_list=[f"{chunk['item_name']}\n{chunk['content']}" for chunk in chunk_list ]
            embeddings= get_bge_m3_embedding(chunk_k_content_list)
            for idx,chunk in enumerate(chunk_list):
                # 字段名必须与下游 node_import_milvus / node_item_name_recognition 保持一致
                chunk["dense_vector"] = embeddings["dense"][idx]
                chunk["sparse_vector"] = embeddings["sparse"][idx]

        # LangGraph 节点必须返回 dict 来更新 state，不能直接返回 list
        return {"chunks": chunks}

if __name__=='__main__':
    node=NodeBGEEmbedding()
    chunks_path = r'D:\code\uv1\data\hak180产品安全手册\chunks_item.json'
    with open(chunks_path, 'r', encoding='utf-8') as f:
        chunks=json.load(f)
    state={
        'chunks':chunks
    }
    res=node(state)
    # 把带向量的切片写回磁盘，供下游 node_import_milvus 读取
    with open(chunks_path, 'w', encoding='utf-8') as f:
        f.write(json_tool(res))
    logger.info(f'向量化完成，已写回 {chunks_path}，共 {len(res)} 条')