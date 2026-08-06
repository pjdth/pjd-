"""
    @Author:th
    @Time:2026/8/6
    @Desc:
"""
import base64
import json
import os
import re
import time
from collections import deque
from pathlib import Path

from langchain.chat_models import init_chat_model
from openai import api_key

from atguigu.config.config import LLMConfig
from atguigu.tool.json_tool import json_tool
from atguigu.tool.logger import logger

def get_md(state):
    md_path=state.get("md_path",'')
    if not md_path:
        raise ValueError("未输入md文件路径，请输入md文件路径")
    md_path_obj=Path(md_path)
    if not md_path_obj.exists():
        raise FileNotFoundError("输入文件不存在")
    images_path=md_path_obj.parent / "images"
    images_path_dir_obj=Path(images_path)
    if not images_path_dir_obj.exists():
        logger.error(f"{images_path}目录不存在,没有图片")
    images_list=os.listdir(images_path)
    #print(images_list)
    if not images_list:
        logger.error(f"{images_path}目录为空")
    return images_list,md_path_obj,images_path_dir_obj

def get_image_pre_after_list(images_list,md_path_obj,images_path_dir_obj):
    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
    with open(md_path_obj, 'r', encoding="utf-8") as f:
        md_content = f.read()
    image_pre_after_list=[]
    for image_name in images_list:
        if Path(image_name).suffix.lower() not in IMAGE_EXTENSIONS:
            logger.warning(f"图片{image_name}不支持格式")
            continue
        pattern = re.compile(r"!\[.*?\]\(.*?" + re.escape(image_name) + r"\)")
        #print(f"图片在文件中为{pattern}")#re.compile('!\\[.*?\\]\\(.*?f3349cded08d6686a93d0a81b9a64ec1e50d9a82cbb88541b37027f085813a15\\.jpg\\)')
        true_image = pattern.search(md_content)
        #print(f"图片在文件中为{true_image}")# 图片在文件中为<re.Match object; span=(0, 0), match=''>
        if not true_image:
            logger.warning(f"图片{image_name}未找到")
            continue
        start,end=true_image.span()
        trip=250
        pre_text=md_content[max(0,start-trip):start]
        after_text=md_content[end:min(len(md_content),end+trip)]
        image_pre_after_list.append({
            "image_name":image_name,
            "pre_text":pre_text,
            "after_text":after_text,
            "image_path":str(images_path_dir_obj / image_name)
        })
    return image_pre_after_list

def get_image_summary_list(image_pre_after_list):
    llm=init_chat_model(
        model=LLMConfig.vl_model,
        model_provider="openai",
        api_key=LLMConfig.openai_api_key,
        base_url=LLMConfig.openai_api_base,
    )
    dp=deque(maxlen=3000)
    for image in image_pre_after_list:
        join_time=time.time()
        if len(dp)==dp.maxlen:
            wait_time=60- (join_time-dp[0])
            if wait_time>0:
                time.sleep(wait_time)
            dp.popleft()
            join_time=time.time()
        dp.append(join_time)

        #处理图片
        with open(image["image_path"], 'rb') as f:
            image_data=f.read()
        base64_str=base64.b64encode(image_data)

        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_str.decode('utf-8')}"}
                },
                {
                    "type": "text",
                    "text": f"这是一张图片，图片上文部分为{image.get('pre_text')}，图片下文部分为{image.get('after_text')}，请用中文简要总结这张图片的摘要，字数在50字以内。"
                }
            ]
        }]
        res=llm.invoke(messages)
        image["summary"] = res.content
        image.pop("pre_text")
        image.pop("after_text")
    return image_pre_after_list

if __name__ == '__main__':
    state={
        "md_path":r"D:\code\uv1\data\out\hak180产品安全手册我是红神\hak180产品安全手册我是红神.md",
        "local_file_path":r"D:\code\uv1\data\out"
    }
    images_list,md_path_obj,images_path_dir_obj=get_md(state)

    image_pre_after_list=get_image_pre_after_list(images_list,md_path_obj,images_path_dir_obj)

    image_summary_list=get_image_summary_list(image_pre_after_list)

    print(json_tool(image_summary_list))

