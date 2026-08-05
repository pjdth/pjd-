import json
import re
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

from atguigu.import_process.base import NodeBase
from atguigu.import_process.state import ImportGraphState
from atguigu.tool.json_tool import json_tool
from atguigu.tool.logger import logger


class NodeDocumentSplit(NodeBase):
    """
    文档切分节点：智能文档切片
    """
    name = "node_document_split"

    def pre_process(self,state):
        md_path = state.get("md_path", '')
        if not md_path:
            raise ValueError("未输入md文件路径，请输入md文件路径")
        md_path_obj = Path(md_path)
        if not md_path_obj.exists():
            raise FileNotFoundError("输入文件不存在")

        file_title = state.get("file_title", '')

        with open(md_path_obj, 'r', encoding="utf-8") as f:
            md_content = f.read()

        if not md_content:
            logger.error("md文件内容为空")
            raise ValueError("md文件内容为空")

        return md_path,md_path_obj,file_title,md_content

    def get_first_split_list(self,md_content,file_title):
        md_content = md_content.replace('\r\n', '\n').replace('\r', '\n')
        # 按行分割，粗切
        md_content_list = md_content.split('\n')
        print(md_content_list)
        first_split_list = []
        is_block = False
        maker = None
        title_idx = 0
        code_pattern = r"^(`{3,}|~{3,})"
        title_pattern = r'^\s*#{1,6}\s+.+'
        for idx, line in enumerate(md_content_list):
            line = line.strip()  # 删空格
            match = re.match(code_pattern, line)
            # print(match)
            # 判断两个符号是否一致，进入了代码块
            if match:
                if not is_block:
                    maker = match.group(1)
                    is_block = True
                    logger.info(f"进入代码块")
                else:
                    if match.group(1) == maker:
                        is_block = False
                        maker = None
                        logger.info(f"退出代码块")
            if not is_block and re.match(title_pattern, line):
                line_content = '/n'.join(md_content_list[title_idx:idx])
                first_split_list.append({
                    'title': md_content_list[title_idx] if line.startswith('#') else '无标题',
                    'file_title': file_title,
                    'content': line_content
                })
                title_idx = idx
        # 最后一段没有标题需要手动添加
        first_split_list.append({
            'title': md_content_list[title_idx],
            'file_title': file_title,
            'content': '/n'.join(md_content_list[title_idx:])
        })
        return first_split_list

    def get_fin_split_list(self,first_split_list,file_title,md_path_obj):
        max_length = 300
        over_lap = 30
        fin_split_list = []
        spliter = RecursiveCharacterTextSplitter(
            chunk_size=max_length,
            chunk_overlap=over_lap,
            length_function=len
        )
        for first_split in first_split_list:
            title = first_split.get("title", "")
            content = first_split.get("content", "")
            real_content = content[len(title):] if content.startswith('#') else content

            if len(real_content) < max_length:
                fin_split_list.append({
                    **first_split,
                    'part': 0
                })
                continue

            if '<table' in real_content:
                fin_split_list.append({
                    **first_split,
                    'part': 0
                })
                continue

            spliter_list = spliter.split_text(real_content)
            for i, split in enumerate(spliter_list):
                fin_split_list.append({
                    'title': title,
                    'file_title': file_title,
                    'content': title + '\n\n' + split,
                    'part': i,
                })
        # print(json_tool(fin_split_list))

        with open(md_path_obj.parent / 'chunks.json', 'w', encoding="utf-8") as f:
            f.write(json_tool(fin_split_list))
        return fin_split_list

    def process(self, state: ImportGraphState):

        md_path,md_path_obj,file_title,md_content=self.pre_process(state)

        first_split_list = self.get_first_split_list(md_content,file_title)

        fin_split_list = self.get_fin_split_list(first_split_list,file_title,md_path_obj)

        return fin_split_list


if __name__ == '__main__':
    noed=NodeDocumentSplit()
    state={
        "md_path":r"D:\code\uv1\data\out\hak180产品安全手册\hak180产品安全手册_new.md",
        "file_title":"hak180产品安全手册"
    }
    res=noed.process(state)
    print(json_tool(res))
