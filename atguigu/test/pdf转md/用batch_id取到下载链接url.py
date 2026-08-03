"""
    @Author:th
    @Time:2026/8/3
    @Desc:
"""
import time

import requests
from atguigu.config.config import MineruConfig
from atguigu.tool.logger import logger


def get_url(batch_id1):
    token = MineruConfig.mineru_token
    batch_id = batch_id1
    url = f"https://mineru.net/api/v4/extract-results/batch/{batch_id}"
    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    while True:
        start_time=time.time()
        try:
            res = requests.get(url, headers=header)
            if res.status_code != 200:
                raise Exception("获取解析结果的请求失败")
            result=res.json()
            if result["code"] != 0:
                raise Exception("获取解析请求结果失败")
            data=result["data"]["extract_result"][0]
            if data["state"] != "done":
                raise Exception("正在读取文件工作中")
            md_zip_url = data["full_zip_url"]
        except Exception as e:
            if time.time()-start_time>120:
                raise Exception("获取解析结果超时")
            time.sleep(2)
            continue
        else:
            break
    return md_zip_url

if __name__ == '__main__':
    from atguigu.test.pdf转md.拿到batch_id import get_batch
    batch_id=get_batch(pdf_path=r"D:\code\uv1\data\hak180产品安全手册.pdf",
          download_path=r"D:\code\uv1\data\out")
    url=get_url(batch_id)
    logger.info(url)