from fastapi import FastAPI

app=FastAPI(
    title="FastAPI",
    description="A fast API",
    version="0.1.0"
)

@app.get("/hello")
def read_root():
    return {"Hello": "World"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,

    )