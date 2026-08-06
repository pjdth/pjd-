from pathlib import Path

from atguigu.config.config import MineruConfig
from atguigu.import_process.base import NodeBase
from atguigu.import_process.state import ImportGraphState
from atguigu.tool.json_tool import json_tool
from atguigu.tool.logger import logger
#拿到pdf，和输出文件夹路径，判断pdf是否在写了是否在文件夹中，返回pdf_path_obj,load_path_obj
#pdf存在之后，用mineru api上传文件3次判断，1请求是否成功，2请求数据是否存在，3如果上传了多个文件，查看多个文件上传成功，拿到batch_id
#拿到batch_id，用bath_id一次一次去请求拿到下载url
#拿到url之后用requests下载文件，判断请求是否成功，判断保存文件地址是否存在，保存文件，再解压文件，如果解压文件存在，先删除再解压保存，解压后再修改full.md文件名字


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
        if not load_path_obj.exists():
            load_path_obj.mkdir(parents=True,exist_ok=True)
        return pdf_path,pdf_path_obj,load_path_obj

    def up_pdf(self,pdf_path_obj,load_path_obj):
        from dotenv import load_dotenv
        import requests
        load_dotenv(override=True)

        token = MineruConfig.mineru_token
        url = "https://mineru.net/api/v4/file-urls/batch"
        logger.info(f"上传pdf请求开始，token:{token},url:{url}")
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

    def get_md_zip_url(self, batch_id):

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
                    raise Exception("正在读取文件工作中")
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

    def download_pdf(self, md_zip_url, local_dir_obj, pdf_path_obj):
        import requests
        md_zip_res = requests.get(md_zip_url)
        if md_zip_res.status_code != 200:
            logger.error("下载PDF文件处理结果zip压缩包请求失败")
            raise Exception(f"下载PDF文件处理结果zip压缩包请求失败")
        md_zip_content = md_zip_res.content

        md_zip_path_obj = local_dir_obj / f"{pdf_path_obj.stem}.zip"

        with open(md_zip_path_obj, 'wb') as f:
            f.write(md_zip_content)

        import zipfile
        import shutil
        unzip_file_content = zipfile.ZipFile(md_zip_path_obj)
        #       解压到哪，构造解压的目的地 路径
        unzip_file_path_obj = local_dir_obj / f"{pdf_path_obj.stem}"

        #       判断解压的目录存在不存在，如果存在先删除，然后再创建
        if unzip_file_path_obj.exists():
            shutil.rmtree(unzip_file_path_obj)
        unzip_file_path_obj.mkdir(parents=True, exist_ok=True)

        #       真正的把解压的内容，放到这个目录
        unzip_file_content.extractall(unzip_file_path_obj)

        #       解压完成后，原本的md文件叫 full.md,我们需要重命名
        origin_md_path_obj = unzip_file_path_obj / "full.md"
        new_md_path_obj = origin_md_path_obj.with_name(f"{pdf_path_obj.stem}.md")  # 在内存当中改了，我们还得落盘
        origin_md_path_obj.rename(new_md_path_obj)

        # 读取Markdown文件内容 存储state
        with open(new_md_path_obj, 'r', encoding="utf-8") as f:
            md_content = f.read()
        return md_content, new_md_path_obj

    def process(self, state: ImportGraphState):
        # 第一大步：校验pdf路径的存在
        pdf_path, pdf_path_obj, local_dir_obj = self.check_pdf(state)

        # 第二大步：上传pdf到mineru要获取batch_id
        batch_id = self.up_pdf(pdf_path_obj,local_dir_obj )

        # 第三大步：等待mineru处理完成,我们需要轮询给mineru发请求，获取一个压缩包zip的url
        md_zip_url = self.get_md_zip_url(batch_id)

        # 第四大步：下载zip压缩文件，解压，重命名，把文件的内容读取保存state
        md_content, new_md_path_obj = self.download_pdf(md_zip_url, local_dir_obj, pdf_path_obj)

        return {
            "md_path": str(new_md_path_obj),
            "md_content": md_content
        }


if __name__ == '__main__':
    node=NodePDFToMD()
    my_state={"pdf_path":r"D:\code\uv1\data\hak180产品安全手册.pdf",
              "local_file_path":r"D:\code\uv1\data\out"}
    res=node.process(my_state)
    logger.info(json_tool(res))