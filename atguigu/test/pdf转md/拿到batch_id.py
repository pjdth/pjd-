"""
    @Author:th
    @Time:2026/8/3
    @Desc:
"""
import os
from pathlib import Path

import requests

from atguigu.config.config import MineruConfig
from atguigu.tool.logger import logger


def get_batch(pdf_path,download_path):
    if pdf_path is None:
        raise ValueError("请输入pdf文件路径")
    pdf_path_obj=Path(pdf_path)
    if not pdf_path_obj.exists():
        raise FileNotFoundError("输入文件不存在")

    if download_path is None:
        raise ValueError("请输入文件夹路径")
    download_path_obj=Path(download_path)
    if not download_path_obj.exists():
        download_path_obj.mkdir(parents=True,exist_ok=True)

    token = MineruConfig.mineru_token
    url = "https://mineru.net/api/v4/file-urls/batch"
    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    data = {
        "files": [
            {"name": "demo.pdf", "data_id": "abcd"}
        ],
        "model_version": "vlm"
    }
    file_path = [pdf_path]
    try:
        response = requests.post(url, headers=header, json=data)
        if response.status_code != 200:
            raise Exception("上传pdf请求失败")
        result = response.json()
        if result["code"] != 0:
            raise Exception("上传pdf获取数据失败")
        batch_id = result["data"]["batch_id"]
        urls = result["data"]["file_urls"]

        for i in range(0, len(urls)):
            with open(file_path[i], 'rb') as f:
                res_upload = requests.put(urls[i], data=f)
                if res_upload.status_code == 200:
                    print(f"{urls[i]} upload success")
                else:
                    print(f"{urls[i]} upload failed")
    except Exception as e:
        print(e)
    return batch_id



res=get_batch(pdf_path=r"D:\code\uv1\data\hak180产品安全手册.pdf",
          download_path=r"D:\code\uv1\data\out")
print(res)