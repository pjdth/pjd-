import asyncio

from pydantic import BaseModel,Field
from fastapi import FastAPI, BackgroundTasks
from starlette.middleware.cors import CORSMiddleware
from queue import Queue

from starlette.responses import StreamingResponse


class BodyParam(BaseModel):
    session_id: str = Field(..., description="会话id")
    query: str = Field(..., description="用户问题")
app=FastAPI(
    title="fastapi",
    description="fastapi",
    version="0.1.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
dic={}

@app.post("/send_message")
async def send_message(body: BodyParam, background_tasks: BackgroundTasks):
    session_id=body.session_id
    query=body.query
    dic[session_id]=Queue()
    background_tasks.add_task(process_query, session_id, query)
    return {"message": "现在开始"}
async def process_query(session_id, query):
    dic[session_id].put({"event":"process","data":query})
    dic[session_id].put({"event":"process","data":'我是顶真'})
    dic[session_id].put({"event":"process","data":query})
    dic[session_id].put({"event":"process","data":'我是雪豹'})
    dic[session_id].put({"event":"process","data":query})
    dic[session_id].put({"event":"process","data":'我是管理员'})
    dic[session_id].put({"event":"process","data":query})
    dic[session_id].put({"event":"process","data":'我是凑企鹅'})
    dic[session_id].put({"event":"final","data":'咕咕嘎嘎'})

@app.get('/ssestream/{session_id}')
async def ssestream(session_id: str):
    async def event_generator():
        while True:
            message = dic[session_id].get()
            yield f'event:{message.get("event")}\n'
            yield f'data: {message.get("data")}\n\n'
            await asyncio.sleep(2)
            if message is None:
                break
    return StreamingResponse(event_generator(), media_type="text/event-stream")


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app=app, host='localhost', port=8000)
