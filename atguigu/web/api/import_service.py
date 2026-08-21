"""
    @Author:th
    @Time:2026/8/17
    @Desc:
"""
import datetime
import shutil
import uuid

from fastapi import FastAPI
from fastapi import File
from fastapi import UploadFile
from fastapi import BackgroundTasks
from starlette.middleware.cors import CORSMiddleware
from pathlib import Path

from atguigu.config.config import MinIoConfig
from atguigu.import_process.main_graph import ImportMainGraphRunner
from atguigu.tool.minio_client_tool import get_minio_client
from atguigu.tool.mongo_client_tool import upsert_book, add_import_record, update_import_record
from atguigu.tool.task_utils import add_running_task, add_done_task, update_task_status, TASK_STATUS_PROCESSING, \
    TASK_STATUS_COMPLETED, TASK_STATUS_FAILED, get_task_info

app=FastAPI(
    title="模块接口",
    description="对接各个模块",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许的源
    allow_credentials=True,  # 允许携带cookie
    allow_methods=["*"],  # 允许的请求方法
    allow_headers=["*"],  # 允许的请求头
)

def register_books_from_chunks(chunks):
    """导入成功后，把本次导入的书籍聚合登记到书库（Mongo books 集合，持久化）"""
    books = {}
    for chunk in chunks or []:
        book_name = chunk.get("book_name") or chunk.get("item_name") or ""
        if not book_name:
            continue
        if book_name not in books:
            books[book_name] = {
                "book_name": book_name,
                "author": chunk.get("author", ""),
                "category": chunk.get("category", ""),
                "entry_name": chunk.get("entry_name", ""),
                "duration": chunk.get("duration", ""),
                "content_type": chunk.get("content_type", "书籍简介"),
                "file_titles": [],
                "chunk_count": 0,
            }
        books[book_name]["chunk_count"] += 1
        file_title = chunk.get("file_title", "")
        if file_title and file_title not in books[book_name]["file_titles"]:
            books[book_name]["file_titles"].append(file_title)
    for book_info in books.values():
        upsert_book(book_info)
    return list(books.keys())

def run_main_graph(task_id: str, local_dir: str, local_file_path: str, file_name: str = ""):
    try:
        init_state = {
            "local_file_path": local_file_path,
            "local_dir": local_dir,
            "task_id": task_id,
        }
        update_task_status(task_id, TASK_STATUS_PROCESSING)
        add_import_record({
            "task_id": task_id,
            "file_name": file_name or Path(local_file_path).name,
            "status": "processing",
        })
        final_state = ImportMainGraphRunner.create_run(init_state)#执行main
        # 登记书库 + 更新导入记录为完成
        book_names = register_books_from_chunks(final_state.get("chunks"))
        update_import_record(task_id, "completed", book_names=book_names)
        update_task_status(task_id, TASK_STATUS_COMPLETED)
    except:
        update_import_record(task_id, "failed")
        update_task_status(task_id, TASK_STATUS_FAILED)
        raise
@app.post('/upload')
async def upload_file(
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...)
):
    #生成唯一id uuid task_id
    task_id = str(uuid.uuid4())
    #创建文件夹local_dir
    local_dir=rf'd:\output\{datetime.datetime.now().strftime("%Y%m%d")}'
    #拿到文件夹对象local_dir_obj
    local_dir_obj = Path(local_dir)
    #创建文件名
    local_file_path=f'{local_dir_obj}/{file.filename}'

    if not local_dir_obj.exists():
        local_dir_obj.mkdir(parents=True, exist_ok=True)
    # 上传阶段就置为 processing，避免响应返回后、后台任务启动前轮询到空 status
    update_task_status(task_id, TASK_STATUS_PROCESSING)
    add_running_task(task_id, 'upload_file')
    with open(local_file_path, 'wb') as f:
        shutil.copyfileobj(file.file, f)

    minio_client = get_minio_client()
    minio_client.fput_object(
        bucket_name=MinIoConfig.minio_bucket_name,
        object_name=f'pdf/{datetime.datetime.now().strftime("%Y%m%d")}/{file.filename}',
        file_path=local_file_path
    )
    add_done_task(task_id, 'upload_file')

    background_tasks.add_task(run_main_graph, task_id=task_id, local_dir=local_dir, local_file_path=local_file_path, file_name=file.filename)

    return {"task_id": task_id, "file_name": file.filename, "file_size": file.size}

@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    return get_task_info(task_id)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
