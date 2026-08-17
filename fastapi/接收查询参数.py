"""
    @Author:th
    @Time:2026/8/16
    @Desc:
"""
from fastapi.responses import FileResponse
from fastapi import Query
from fastapi import FastAPI
from fastapi.responses import Response
app=FastAPI()

@app.get("/info")
def get_info(
        name: str = Query(..., description="The name of the person to greet"),
        id: int = Query(..., description="The ID of the person"),
        age: int = Query(description="The age of the person",default=18)
):
    return {"name": name, "id": id, "age": age}

@app.get("/custom")
async def custom_response():
    # 返回二进制数据，指定自定义 MIME 类型
    return Response(
        content="<h1>‘扣1送地狱火’</h1>",
        # media_type="text/plain",
        media_type="text/html",
        status_code=200)

@app.get("/download")
async def download():
    return FileResponse(r"C:\Users\th\Pictures\diy\cpu\Screenshot_2026-08-13-23-03-30-00_149003a2d400f6a.jpg",
                        media_type="image/jpeg",
                        headers={
                            "Content-Disposition": "attachment; filename=123.jpg"
                        })

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="192.168.5.40", port=8000)

