import base64
import json
import os
import re
import time
from collections import deque
from pathlib import Path

from langchain.chat_models import init_chat_model
from openai import api_key
from pymongo.common import MAX_CONNECTING

from atguigu.config.config import LLMConfig
from atguigu.import_process.base import NodeBase
from atguigu.import_process.state import ImportGraphState
from atguigu.tool.logger import logger


class NodeMDImg(NodeBase):
    """
    MarkDown图片处理节点：多模态图片理解
    """

    name = "node_md_img"

    def process(self, state: ImportGraphState):
        md_path=state.get("md_path",'')
        if not md_path:
            raise ValueError("未输入md文件路径，请输入md文件路径")
        md_path_obj=Path(md_path)
        if not md_path_obj.exists():
            raise FileNotFoundError("输入文件不存在")

        with open(md_path_obj, 'r', encoding="utf-8") as f:
            md_content=f.read()
        if not md_content:
            raise ValueError("md文件内容为空")

        images_dir_obj=md_path_obj.parent / "images"
        if not images_dir_obj.exists():
            logger.info("文件中没有图片")
            return md_content

        images_list=os.listdir(images_dir_obj)
        logger.info(f"文件中图片为{images_list}")
        if not images_list:
            logger.info("文件中没有图片")
            return md_content
        MAX_CONNECTING=250
        IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
        image_with_content=[]
        for image_name in images_list:
            if Path(image_name).suffix.lower() not in IMAGE_EXTENSIONS:
                logger.warning(f"图片{image_name}不支持格式")
                continue
            pattern = re.compile(r"!\[.*?\]\(.*?" + re.escape(image_name) + r"\)")
            true_image=pattern.search(md_content)
            logger.info(f"图片在文件中为{true_image}")
            if not true_image:
                logger.warning(f"图片{image_name}未找到")
                continue
            start,end=true_image.span()
            logger.info(f"图片{image_name}在文件中的起始位置为{start}，结束位置为{end}")
            pre_text=md_content[max(0,start-MAX_CONNECTING):start]
            post_text=md_content[end:min(len(md_content),end+MAX_CONNECTING)]
            image_path=str(images_dir_obj / image_name)

            image_with_content.append({
                "image_name":image_name,
                "pre_text":pre_text,
                "post_text":post_text,
                "image_path":image_path
            })
        # print("图片与文件内容关系为")
        # print(json.dumps(image_with_content, ensure_ascii=False, indent=2))

        llm=init_chat_model(
            model=LLMConfig.vl_model,
            model_provider="openai",
            temperature=LLMConfig.llm_default_temperature
        )

        dp=deque(maxlen=50)
        for image in image_with_content:
            join_time = time.time()
            if len(dp) == dp.maxlen:
                wait_time = 60 - (join_time - dp[0])
                if wait_time > 0:
                    time.sleep(wait_time)
                dp.popleft()
            join_time = time.time()
            dp.append(join_time)

            with open(image["image_path"], 'rb') as f:
                image_data = f.read()
                base64_str = base64.b64encode(image_data)

            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_str.decode("utf-8")}",
                            },
                        },
                        {"type": "text", "text": f"""这是一张图片，图片上文部分为"{image.get("pre_text")}"，
                                            下文部分为"{image.get("post_text")}"，请用中文简要总结这张图片的摘要,字数在50字以内。"""},
                    ],
                },
            ]

            res=llm.invoke(messages)
            image["content"] = res.content
            image.pop("pre_text")
            image.pop("post_text")

        print(json.dumps(image_with_content, ensure_ascii=False, indent=2))
if __name__ == '__main__':
    node=NodeMDImg()
    my_state={"md_path":r"D:\code\uv1\data\out\hak180产品安全手册\hak180产品安全手册.md"}
    res=node.process(my_state)
    logger.info(res)