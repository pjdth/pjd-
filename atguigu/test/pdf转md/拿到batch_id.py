"""
    @Author:th
    @Time:2026/8/3
    @Desc:
"""
from pathlib import Path

import requests

from atguigu.config.config import MineruConfig
from atguigu.tool.logger import logger


def get_batch(pdf_path,download_path):
    mineru_token =MineruConfig.mineru_token
    url = "https://mineru.net/api/v4/file-urls/batch"
    pdf_path_obj=Path(pdf_path)
    logger.info(f"上传pdf请求开始，token:{mineru_token},url:{url}")

    token = mineru_token
    url = "https://mineru.net/api/v4/file-urls/batch"
    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    data = {
        "files": [
            {"name": f"{pdf_path_obj.name}", "data_id": "abcd"}
        ],
        "model_version": "vlm"
    }
    file_path = [str(pdf_path_obj)]

    response = requests.post(url, headers=header, json=data)
    if response.status_code != 200:
        raise Exception("上传pdf请求失败")
    result = response.json()
    print('response success. result:{}'.format(result))
    if result["code"] != 0:
        raise Exception("上传pdf获取数据失败")
    batch_id = result["data"]["batch_id"]
    urls = result["data"]["file_urls"]
    print('batch_id:{},urls:{}'.format(batch_id, urls))
    for i in range(0, len(urls)):
        with open(file_path[i], 'rb') as f:
            res_upload = requests.put(urls[i], data=f)
            if res_upload.status_code == 200:
                print(f"{urls[i]} upload success")
            else:
                print(f"{urls[i]} upload failed")
    return batch_id



res=get_batch(pdf_path=r"D:\code\uv1\data\hak180产品安全手册.pdf",
          download_path=r"D:\code\uv1\data\out")
print(res)