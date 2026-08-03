from pathlib import Path

from atguigu.import_process.base import NodeBase
from atguigu.import_process.state import ImportGraphState
from atguigu.tool.json_tool import json_tool
from atguigu.tool.logger import logger


class NodeEntry(NodeBase):
    """
    入口节点：任务分发
    """

    name = "node_entry"

    def process(self, state: ImportGraphState):
        local_file_path=state.get("local_file_path",'')
        if not local_file_path :
            raise ValueError("未输入文件路径，请输入文件路径")
        local_file_path_obj=Path(local_file_path)
        if not local_file_path_obj.exists():
            raise FileNotFoundError("输入文件不存在")
        file_title=local_file_path_obj.stem
        suffix=local_file_path_obj.suffix
        # print(suffix)

        if suffix.lower() == ".pdf":
            state["is_pdf_read_enabled"] = True
            state["file_title"] = file_title
            state["pdf_path"] = str(local_file_path_obj)
            return state

        elif suffix.lower() == ".md":
            state["is_md_read_enabled"] = True
            state["file_title"] = file_title
            state["md_path"] = str(local_file_path_obj)
            return state
        else:
            raise ValueError(f"输入文件格式错误{suffix}")

if __name__ == '__main__':
    node=NodeEntry()
    my_state={"local_file_path":r"D:\code\uv1\data\hak180产品安全手册.pdf"}
    res=node.process(my_state)
    logger.info(json_tool(res))