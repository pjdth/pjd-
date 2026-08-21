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

    @staticmethod
    def _clean_text(text):
        """去除内容中的换行类分隔符（真换行 / 字面 \\n / 字面 /n），连续空白压成单空格。

        书库内容直接展示给用户，任何换行（包括字面转义字符）都会破坏阅读排版，
        故在导入阶段就把 content/title 统一清理干净再入库。
        """
        if not text:
            return ""
        s = str(text).replace("\\n", " ").replace("\\r", " ").replace("/n", " ").replace("/r", " ")
        return re.sub(r"\s+", " ", s).strip()

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

    def parse_book_metadata(self, md_content):
        """解析 MD 文件元数据区（书名/作者名/条目名称/类别标签）与全文时长。
        源文件格式示例：
            ## 元数据
            - 书名：三体
            - 作者名：刘慈欣
            - 条目名称：全书
            - 类别/标签：科幻, 宇宙文明, 悬疑
        """
        book_name, author, entry_name, category = "", "", "", ""
        meta_match = re.search(r'##\s*元数据\s*\n(.*?)(?=\n##|\Z)', md_content, re.S)
        if meta_match:
            for line in meta_match.group(1).splitlines():
                line = line.strip().lstrip('-').strip()
                m = re.match(r'^(书名|作者名|条目名称|类别/标签)[：:]\s*(.+)$', line)
                if m:
                    key, val = m.group(1), m.group(2).strip()
                    if key == "书名":
                        book_name = val
                    elif key == "作者名":
                        author = val
                    elif key == "条目名称":
                        entry_name = val
                    elif key == "类别/标签":
                        category = val
        # 时长：全文正则提取 "时长约 X 小时"
        duration = ""
        d = re.search(r'时长\s*约?\s*(\d+(?:\.\d+)?)\s*小时', md_content)
        if d:
            duration = f"{d.group(1)}小时"
        return {
            "book_name": book_name,
            "author": author,
            "entry_name": entry_name,
            "category": category,
            "duration": duration,
        }

    def map_content_type(self, title):
        """根据切片标题（MD 二级标题）映射内容类型（对齐需求文档 §5）"""
        for keyword, content_type in [
            ("有声书", "有声书信息"),
            ("作者介绍", "作者介绍"),
            ("听书笔记", "听书笔记"),
            ("评论摘要", "用户评论摘要"),
            ("常见问答", "常见问答"),
            ("推荐语", "推荐运营资料"),
        ]:
            if keyword in (title or ""):
                return content_type
        return "书籍简介"

    def get_first_split_list(self,md_content,file_title):
        md_content = md_content.replace('\r\n', '\n').replace('\r', '\n')
        # 按行分割，粗切
        md_content_list = md_content.split('\n')
        print(md_content_list)
        first_split_list = []
        is_code=[]
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
                # if not is_block:
                #     maker = match.group(1)
                #     is_block = True
                #     logger.info(f"进入代码块")
                # else:
                #     if match.group(1) == maker:
                #         is_block = False
                #         maker = None
                #         logger.info(f"退出代码块")
                if match:
                    if not is_code:
                        is_code.append(match.group(1))
                    elif match.group(1) != is_code[-1]:
                        is_code.append(match.group(1))
                    else:
                        is_code.pop()
            # if not is_block and re.match(title_pattern, line):
            if not is_code and re.match(title_pattern, line):
                line_content = ' '.join(md_content_list[title_idx:idx])
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
            'content': ' '.join(md_content_list[title_idx:])
        })
        return first_split_list

    def get_fin_split_list(self,first_split_list,file_title,md_path_obj,meta=None):
        max_length = 300
        over_lap = 30
        meta = meta or {}
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
                    'part': 0,
                    # 需求 §5 元数据字段：书名/作者/条目/类别/类型/时长
                    'book_name': meta.get("book_name", ""),
                    'author': meta.get("author", ""),
                    'entry_name': meta.get("entry_name", ""),
                    'category': meta.get("category", ""),
                    'duration': meta.get("duration", ""),
                    'content_type': self.map_content_type(title),
                })
                continue

            if '<table' in real_content:
                fin_split_list.append({
                    **first_split,
                    'part': 0,
                    'book_name': meta.get("book_name", ""),
                    'author': meta.get("author", ""),
                    'entry_name': meta.get("entry_name", ""),
                    'category': meta.get("category", ""),
                    'duration': meta.get("duration", ""),
                    'content_type': self.map_content_type(title),
                })
                continue

            spliter_list = spliter.split_text(real_content)
            for i, split in enumerate(spliter_list):
                fin_split_list.append({
                    'title': title,
                    'file_title': file_title,
                    'content': title + ' ' + split,
                    'part': i,
                    'book_name': meta.get("book_name", ""),
                    'author': meta.get("author", ""),
                    'entry_name': meta.get("entry_name", ""),
                    'category': meta.get("category", ""),
                    'duration': meta.get("duration", ""),
                    'content_type': self.map_content_type(title),
                })
        # 统一兜底：content/title 里不允许出现任何换行类字符（真换行/字面 \n/字面 /n）
        for chunk in fin_split_list:
            chunk['content'] = self._clean_text(chunk.get('content'))
            chunk['title'] = self._clean_text(chunk.get('title'))
        # print(json_tool(fin_split_list))

        with open(md_path_obj.parent / 'chunks.json', 'w', encoding="utf-8") as f:
            f.write(json_tool(fin_split_list))
        return fin_split_list

    def process(self, state: ImportGraphState):

        md_path,md_path_obj,file_title,md_content=self.pre_process(state)

        # 解析元数据（书名/作者/条目/类别/时长），随切片一起入库
        meta = self.parse_book_metadata(md_content)

        first_split_list = self.get_first_split_list(md_content,file_title)

        fin_split_list = self.get_fin_split_list(first_split_list,file_title,md_path_obj,meta)

        return {
            "chunks": fin_split_list,
        }


if __name__ == '__main__':
    noed=NodeDocumentSplit()
    state={
        "md_path":r"D:\code\uv1\data\out\hak180产品安全手册\hak180产品安全手册_new.md",
        "file_title":"hak180产品安全手册"
    }
    res=noed.process(state)
    print(json_tool(res))
