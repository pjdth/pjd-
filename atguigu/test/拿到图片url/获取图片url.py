"""
    @Author:th
    @Time:2026/8/6
    @Desc:
"""
import re

from minio.deleteobjects import DeleteObject

from atguigu.config.config import MinIoConfig
from atguigu.test.拿到图片摘要.拿到摘要 import get_image_summary_list, get_md, get_image_pre_after_list
from atguigu.tool.minio_client_tool import get_minio_client


def get_image_url(image_summary_list):
    minio_client=get_minio_client()#拿到连接
    up_image_path = MinIoConfig.minio_img_dir# minio中图片上传的目录
    old_minio_images=minio_client.list_objects(bucket_name=MinIoConfig.minio_bucket_name,
                              prefix=up_image_path,
                              recursive= True)
    #print(old_minio_images)#一个生成器
    del_list=[DeleteObject(old_image_obj.object_name) for old_image_obj in old_minio_images]
    errors=minio_client.remove_objects(
        bucket_name=MinIoConfig.minio_bucket_name,
        delete_object_list=del_list,
    )
    if errors:
        for error in errors:
            print(f'删除图片为{error}')

    image_url_list=[]

    for image_summary in image_summary_list:
        minio_client.fput_object(
            bucket_name=MinIoConfig.minio_bucket_name,
            object_name=f'{up_image_path}/{image_summary["image_name"]}',
            file_path=image_summary["image_path"],
            )
        image_url_list.append({
            **image_summary,
            "image_url": f'http://{MinIoConfig.minio_endpoint}/{MinIoConfig.minio_bucket_name}/{MinIoConfig.minio_img_dir}/{image_summary["image_name"]}',
        })
    return image_url_list

def update_md_file(image_url_list, md_path_obj):
    md_content=md_path_obj.read_text(encoding="utf-8")
    for image_with_summary_url in image_url_list:
        pattern = re.compile(r"!\[.*?\]\(.*?" + re.escape(image_with_summary_url["image_name"]) + r"\)")
        md_content=pattern.sub(f"![{image_with_summary_url['summary']}]({image_with_summary_url['image_url']})", md_content)
    new_md_path_obj=md_path_obj.parent / (str(md_path_obj.stem) + "_new.md")
    new_md_path_obj.write_text(md_content, encoding="utf-8")



if __name__ == '__main__':
    state = {
        "md_path": r"D:\code\uv1\data\out\hak180产品安全手册我是红神\hak180产品安全手册我是红神.md",
        "local_file_path": r"D:\code\uv1\data\out"
    }
    images_list, md_path_obj, images_path_dir_obj = get_md(state)

    image_pre_after_list = get_image_pre_after_list(images_list, md_path_obj, images_path_dir_obj)

    image_summary_list = get_image_summary_list(image_pre_after_list)

    image_url_list=get_image_url(image_summary_list)

    update_md_file(image_url_list, md_path_obj)