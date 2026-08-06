"""
    @Author:th
    @Time:2026/8/3
    @Desc:
"""
import os
from pathlib import Path

from atguigu.tool.logger import logger


def download_md(md_zip_url,download_dir_obj,pdf_path_obj):
    import requests
    res=requests.get(md_zip_url)
    if res.status_code != 200:
        logger.error("下载PDF文件处理结果zip压缩包请求失败")
        raise Exception(f"下载PDF文件处理结果zip压缩包请求失败")
    md_zip_content=res.content
    #print(md_zip_content)
    if download_dir_obj is None:
        raise ValueError("请输入下载目录")
    if not download_dir_obj.exists():
        download_dir_obj.mkdir(parents=True,exist_ok=True)
    zip_path_obj=download_dir_obj / f"{pdf_path_obj.stem}我是红神.zip"
    if zip_path_obj.exists():
        zip_path_obj.unlink()
    with open(zip_path_obj,'wb') as f:
        f.write(md_zip_content)

    import zipfile
    import shutil
    unzip_file_content=zipfile.ZipFile(zip_path_obj)
    zip_path_dir_path=zip_path_obj.parent/f"{zip_path_obj.stem}"
    if zip_path_dir_path.exists():
        shutil.rmtree(zip_path_dir_path)
    zip_path_dir_path.mkdir(parents=True,exist_ok=True)
    unzip_file_content.extractall(zip_path_dir_path)

    #修改full.md文件名
    old_md_name=zip_path_dir_path / "full.md"
    old_md_name_obj=Path(old_md_name)
    new_md_name=old_md_name_obj.with_name(f"{zip_path_obj.stem}.md")
    old_md_name_obj.rename(new_md_name)

    with open(new_md_name,'r',encoding="utf-8") as f:
        md_content=f.read()
    return md_content,Path(new_md_name)



if __name__ == '__main__':
    from atguigu.test.pdf转md.拿到batch_id import get_batch
    from atguigu.test.pdf转md.用batch_id取到下载链接url import get_url
    batch_id=get_batch(pdf_path=r"D:\code\uv1\data\hak180产品安全手册.pdf",
          download_path=r"D:\code\uv1\data\out")
    md_zip_url=get_url(batch_id)
    pdf_path_obj=Path(r"D:\code\uv1\data\hak180产品安全手册.pdf")
    download_dir_obj=Path(r"D:\code\uv1\data\out")
    logger.info(download_md(md_zip_url,download_dir_obj,pdf_path_obj))