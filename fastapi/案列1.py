import queue
import time

from fastapi import FastAPI, BackgroundTasks
from queue import Queue

from fastapi.params import Query
from starlette.responses import StreamingResponse

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="FastAPI",
    description="A fast API",
    version="0.1.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # 开发阶段先全放开；上线换成具体域名，比如 ["http://localhost:63342"]
    allow_methods=["*"],
    allow_headers=["*"],
)
queue_dict={}

def make_email(session_id: str):
    queue_dict[session_id].put("我不是红神1")
    queue_dict[session_id].put("我不是红神2")
    queue_dict[session_id].put("我不是红神3")
    queue_dict[session_id].put("我不是红神4")
    queue_dict[session_id].put("我不是红神5")
    queue_dict[session_id].put("我不是红神6")
    queue_dict[session_id].put(None)

@app.get("/send_message")
def send_message(session_id: str,background_tasks: BackgroundTasks):
    if session_id not in queue_dict:
        queue_dict[session_id] = queue.Queue()

    background_tasks.add_task(make_email, session_id)

    return {
        "session_id": session_id,
        "message": "开始生成邮件添加队列"
    }

@app.get("/ssestream")
async def ssestream(session_id: str = Query(...,description="会话编号")):
    def send_email(session_id: str):
        queue_obj = queue_dict[session_id]
        while True:
            email = queue_obj.get()
            time.sleep(1)
            yield f"data:{email}\n\n"
            if email is None:
                break
    return StreamingResponse(send_email(session_id), media_type="text/event-stream")


@app.get("/hello")
def read_root():
    return {"Hello": "World"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        app,
        host="192.168.5.40",
        port=8000,
    )
