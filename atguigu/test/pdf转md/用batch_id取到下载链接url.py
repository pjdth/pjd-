"""
    @Author:th
    @Time:2026/8/3
    @Desc:
"""
import requests
from atguigu.config.config import MineruConfig

def get_url(batch_id1):
    token = MineruConfig.mineru_token
    batch_id = batch_id1
    url = f"https://mineru.net/api/v4/extract-results/batch/{batch_id}"
    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    while True:
        res = requests.get(url, headers=header)


if __name__ == '__main__':
    from atguigu.test.pdf转md.拿到batch_id import get_batch
    batch_id=get_batch(pdf_path=r"D:\code\uv1\data\hak180产品安全手册.pdf",
          download_path=r"D:\code\uv1\data\out")
    url=get_url(batch_id)