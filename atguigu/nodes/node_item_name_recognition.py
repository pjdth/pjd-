import json

from atguigu.import_process.base import NodeBase
from atguigu.import_process.state import ImportGraphState
from atguigu.tool.logger import logger


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
        print(content_str)
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