import queue
import time

from fastapi import FastAPI, BackgroundTasks
from fastapi.params import Query
from queue import Queue

from starlette.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse

app=FastAPI(
    title="fastapi",
    description="fastapi",
    version="0.1.0"
)
dict={}
def send_email1(session_id):
    dict[session_id].put('我是红神1')
    dict[session_id].put('我是红神2')
    dict[session_id].put('我是红神3')
    dict[session_id].put(None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get('/send_emil')
def send_email(background_tasks: BackgroundTasks,
              session_id: str=Query(...)):
    dict[session_id]=Queue()
    background_tasks.add_task(send_email1, session_id)
    return {"message": "开始制造邮件"}

@app.get('/ssestream')
def ssestream(session_id: str=Query(...)):
    def send_to_up():

        while True:
            email = dict[session_id].get()
            yield f'data: {email}\n\n'
            time.sleep(1)
            if email is None:
                break
    return StreamingResponse(send_to_up(), media_type="text/event-stream")
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app=app, host='localhost', port=8000)

