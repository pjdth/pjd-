"""
    @Author:th
    @Time:2026/8/3
    @Desc:
"""
from pathlib import Path


def download_md(md_zip_url,local_dir_obj,pdf_path_obj):
    import requests
    md_zip_res=requests.get(md_zip_url)
    print('-----------------------------------------------')
    # print(md_zip_res)
    md_zip_content=md_zip_res.content
    if md_zip_res.status_code!=200:
        raise Exception("下载PDF文件处理结果zip压缩包请求失败")
    # print(md_zip_content)
    download_dir=local_dir_obj / f"{pdf_path_obj.stem}我是红神.zip"
    with open(download_dir,'wb') as f:
        f.write(md_zip_content)
    import zipfile
    import shutil
    zip_content=zipfile.ZipFile(download_dir)
    unzip_file_path_obj=local_dir_obj / f"{pdf_path_obj.stem}我是红神"
    if unzip_file_path_obj.exists():
        shutil.rmtree(unzip_file_path_obj)
    unzip_file_path_obj.mkdir(parents=True,exist_ok=True)
    zip_content.extractall(unzip_file_path_obj)




if __name__ == '__main__':
    from atguigu.test.pdf转md.拿到batch_id import get_batch
    from atguigu.test.pdf转md.用batch_id取到下载链接url import get_url
    batch_id=get_batch(pdf_path=r"D:\code\uv1\data\hak180产品安全手册.pdf",
          download_path=r"D:\code\uv1\data\out")
    md_zip_url=get_url(batch_id)
    pdf_path_obj=Path(r"D:\code\uv1\data\hak180产品安全手册.pdf")
    local_dir_obj=Path(r"D:\code\uv1\data\out")
    download_md(md_zip_url,local_dir_obj,pdf_path_obj)