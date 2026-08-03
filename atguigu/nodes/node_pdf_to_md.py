from pathlib import Path

from atguigu.config.config import MineruConfig
from atguigu.import_process.base import NodeBase
from atguigu.import_process.state import ImportGraphState
from atguigu.tool.json_tool import json_tool
from atguigu.tool.logger import logger



class NodePDFToMD(NodeBase):
    """
    PDF 转 Markdown 节点：PDF结构化解析
    """

    name = "node_pdf_to_md"

    def check_pdf(self,state:ImportGraphState):
        pdf_path=state.get("pdf_path",'')
        load_path=state.get("local_file_path",'')
        if not pdf_path:
            raise ValueError("未输入PDF文件路径，请输入PDF文件路径")
        pdf_path_obj=Path(pdf_path)
        if not pdf_path_obj.exists():
            raise FileNotFoundError("输入文件不存在")
        load_path_obj=Path(load_path)
        if load_path_obj.exists():
            load_path_obj.mkdir(parents=True,exist_ok=True)
        return pdf_path_obj,load_path_obj

    def up_pdf(self,state:ImportGraphState):
        pdf_path_obj,load_path_obj=self.check_pdf(state)
        from dotenv import load_dotenv
        import requests
        load_dotenv(override=True)

        token = MineruConfig.mineru_token
        url = f"{MineruConfig.mineru_url}/file-urls/batch"
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
        if result["code"] != 0:
            raise Exception("上传pdf获取数据失败")
        batch_id = result["data"]["batch_id"]

        urls = result["data"]["file_urls"]
        #批量上次文件
        for i in range(0, len(urls)):
            with open(file_path[i], 'rb') as f:
                res_upload = requests.put(urls[i], data=f)
                if res_upload.status_code == 200:
                    logger.info(f"{urls[i]}上传成功")
                else:
                    logger.error(f"{urls[i]}上传失败")

        return batch_id

    def download_md_zip_url(self, batch_id):


        import requests
        import time
        total_time = 120
        current_time = 0
        token = MineruConfig.mineru_token
        batch_id = batch_id
        url = f"https://mineru.net/api/v4/extract-results/batch/{batch_id}"
        header = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        while True:
            start_time = time.time()
            try:
                res = requests.get(url, headers=header)
                if res.status_code != 200:
                    raise Exception("获取解析结果的请求失败")
                result = res.json()
                if result["code"] != 0:
                    raise Exception("获取解析请求结果失败")
                data = result["data"]["extract_result"][0]

                if data["state"] != "done":
                    raise Exception("获取解析结果错误")
                md_zip_url = data["full_zip_url"]
            except Exception as e:
                logger.error(f"获取解析结果失败{e}，正在重试")
                current_time += time.time() - start_time
                if current_time > total_time:
                    raise Exception("获取解析结果超时")

                time.sleep(2)
                continue
            else:
                break

        logger.info(f"获取解析结果成功,{md_zip_url}")
        return md_zip_url

    def download_pdf(self, md_zip_url, local_dir_path_obj, pdf_path_obj):
        pass

    def process(self, state: ImportGraphState):
        pass

if __name__ == '__main__':
    node=NodePDFToMD()
    my_state={"pdf_path":r"D:\code\uv1\data\hak180产品安全手册.pdf",
              "local_file_path":r"D:\code\uv1\data\out"}
    res=node.process(my_state)
    logger.info(json_tool(res))