"""
    @Author:th
    @Time:2026/8/18
    @Desc:
"""
import json
import time
import uuid

from fastapi import FastAPI, Path, BackgroundTasks, Body

from pydantic import BaseModel,Field
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse

from atguigu.query_process.nodes.main_graph import QueryMainGraphRunner
from atguigu.tool.logger import logger
from atguigu.tool.mongo_client_tool import get_history_list, clear_history_list
from atguigu.tool.task_utils import get_data,TASK_STATUS_PROCESSING, TASK_STATUS_COMPLETED, \
    TASK_STATUS_FAILED, put_data, get_task_info, update_task_status, create_queue

app=FastAPI(
    title="Query Service",
    description="A query service",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/health")
def read_root():
    return {"message": "Hello World"}

@app.get("/history/{session_id}")
def get_history(session_id: str=Path(...,description="The session id")):
    history_list=get_history_list(session_id)
    history_list=[
        {
            "_id":str(item.get("_id")),
            "role":item.get("role",""),
            "text":item.get("text",""),
            "rewritten_query":item.get("rewritten_query",""),
            "item_names":item.get("item_names",""),
            "ts":item.get("ts",""),
            "session_id":item.get("session_id","")
        }
        for item in history_list
    ]
    history_list.sort(key=lambda a: a.get("ts"))
    return {"items": history_list}

@app.delete("/history/{session_id}")
def delete_history(session_id: str=Path(...,description="The session id")):
    clear_history_list(session_id)
    return {"msg": "删除成功"}

class QueryParams(BaseModel):
    query: str = Field(..., description="查询内容")
    session_id: str = Field(..., description="会话ID")

@app.post("/query")
def query(background_tasks:BackgroundTasks,
          query_params: QueryParams=Body(...,description="查询请求体参数"),
          ):
    task_id=str(uuid.uuid4())
    original_query = query_params.query
    session_id = query_params.session_id
    create_queue(task_id)
    background_tasks.add_task(run_main_graph, task_id, original_query, session_id)
    return {
        "task_id": task_id,
        "original_query": original_query,
        "session_id": session_id
    }
def _friendly_error_message(e):
    """把底层异常转成用户能看懂的话，避免直接把 Milvus/网络内部错误抛给前端"""
    s = str(e)
    if "collection not found" in s or "CollectionNotExists" in s:
        return "知识库还没有内容，请先通过导入服务上传书籍资料（PDF/MD），再重新提问。"
    if "network" in s.lower() or "connection" in s.lower() or "timeout" in s.lower():
        return "网络连接异常，请稍后重试。"
    if "milvus" in s.lower() or "index" in s.lower():
        return "知识库服务暂时不可用，请稍后重试。"
    return f"服务开小差了，请稍后重试。({s[:80]})"

def run_main_graph(task_id, original_query, session_id):
    try:
        init_state={
            'task_id': task_id,
            'original_query': original_query,
            'session_id': session_id
        }
        update_task_status(task_id,TASK_STATUS_PROCESSING)
        put_data(task_id, "progress",get_task_info(task_id))   # 与前端 chat.html 的 'progress' 监听器对齐

        QueryMainGraphRunner().create_and_run(init_state)

        update_task_status(task_id, TASK_STATUS_COMPLETED)
        put_data(task_id, "progress",get_task_info(task_id))   # status=completed 时前端会清掉“...”态
    except Exception as e:
        update_task_status(task_id, TASK_STATUS_FAILED)
        # 把错误转成友好提示推给前端（'error' 监听器会展示），不再裸抛，避免 500 刷屏
        msg = _friendly_error_message(e)
        put_data(task_id, "error", {"error": msg, "status": TASK_STATUS_FAILED})
        logger.error(f"Error in run_main_graph: {e}")

@app.get('/stream/{task_id}')
async def stream(task_id: str=Path(...,description="The task id")):
    return StreamingResponse(generate_stream(task_id), media_type="text/event-stream")
def generate_stream(task_id):
    while True:
        item = get_data(task_id)            # 阻塞直到后台任务 push 数据
        event = item.get("event", "")
        data = item.get("data", {})
        yield f"event: {event}\n"
        yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
        if event in ("error", "failed") or data.get("status") in (TASK_STATUS_COMPLETED, TASK_STATUS_FAILED):
            break

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8001,
    )
