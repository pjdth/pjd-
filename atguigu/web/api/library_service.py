"""
    @Author:th
    @Desc: 书库服务：书籍列表 / 书籍详情 / 章节内容 / 文字转语音 / 导入记录
    端口 8002，与导入服务(8000)、查询服务(8001)独立。
    书库与导入记录持久化在 MongoDB（books / import_records 集合），刷新页面不丢失。
"""
import re
import time

from fastapi import FastAPI, HTTPException, Body, UploadFile, File, Form
from pydantic import BaseModel, Field
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import Response

from atguigu.config.config import MilvusConfig
from atguigu.tool.logger import logger
from atguigu.tool.milvus_client_tool import get_milvus_client, collection_exists
from atguigu.tool.mongo_client_tool import (
    list_books, get_book, upsert_book, list_import_records,
    save_tts_voice, get_tts_voice, list_tts_voices,
)
from atguigu.tool.tts_tool import synthesize, get_voices, create_cloned_voice, synthesize_clone

app = FastAPI(
    title="Library Service",
    description="书库与文字转语音服务",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _clean_mongo_record(item):
    """Mongo 文档转 JSON 可序列化结构"""
    return {
        key: value
        for key, value in item.items()
        if key != "_id" and value is not None
    }


def _clean_text(text):
    """去掉文本中的换行类字符（真换行 / 字面 \\n / 字面 /n），统一为单个空格并压缩连续空白。
    书库内容直接展示给用户，换行会破坏阅读排版，故在返回前统一清理（兼容历史导入数据）。"""
    if not text:
        return ""
    s = str(text).replace("\\n", " ").replace("\\r", " ").replace("/n", " ").replace("/r", " ")
    return re.sub(r"\s+", " ", s).strip()


def _backfill_books_from_milvus():
    """书库为空时，从 Milvus 切片集合回填已导入的书籍（兼容未走新登记流程的历史数据）"""
    try:
        if list_books():
            return
        if not collection_exists(MilvusConfig.chunks_collection):
            return
        mc = get_milvus_client()
        res = mc.query(
            collection_name=MilvusConfig.chunks_collection,
            filter='book_name != ""',
            output_fields=["book_name", "author", "category", "entry_name",
                           "duration", "content_type", "file_title", "item_name"],
            limit=1000,
        )
        books = {}
        for row in res:
            book_name = row.get("book_name") or row.get("item_name") or ""
            if not book_name:
                continue
            if book_name not in books:
                books[book_name] = {
                    "book_name": book_name,
                    "author": row.get("author", ""),
                    "category": row.get("category", ""),
                    "entry_name": row.get("entry_name", ""),
                    "duration": row.get("duration", ""),
                    "content_type": row.get("content_type", "书籍简介"),
                    "file_titles": [],
                    "chunk_count": 0,
                }
            books[book_name]["chunk_count"] += 1
            ft = row.get("file_title", "")
            if ft and ft not in books[book_name]["file_titles"]:
                books[book_name]["file_titles"].append(ft)
        for book_info in books.values():
            upsert_book(book_info)
        logger.info(f"从 Milvus 回填书库 {len(books)} 本")
    except Exception as e:
        logger.warning(f"从 Milvus 回填书库失败（可忽略）: {e}")


@app.get("/api/books")
def get_books():
    """书库列表：书名/作者/类别/时长/切片数/导入时间"""
    _backfill_books_from_milvus()
    books = list_books()
    return {"items": [_clean_mongo_record(b) for b in books]}


@app.get("/api/books/{book_name}")
def get_book_detail(book_name: str):
    """单本书基本信息"""
    book = get_book(book_name)
    if not book:
        raise HTTPException(status_code=404, detail=f"书库中不存在《{book_name}》")
    return _clean_mongo_record(book)


@app.get("/api/books/{book_name}/sections")
def get_book_sections(book_name: str):
    """书的章节/切片列表（来自 Milvus 知识库），供页面展示与朗读"""
    if not collection_exists(MilvusConfig.chunks_collection):
        raise HTTPException(status_code=404, detail="知识库尚未导入内容")
    mc = get_milvus_client()
    safe = book_name.replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"')
    try:
        res = mc.query(
            collection_name=MilvusConfig.chunks_collection,
            filter=f'book_name == "{safe}"',
            output_fields=["title", "content", "content_type", "author", "part", "item_name"],
            limit=500,
        )
        if not res:
            res = mc.query(
                collection_name=MilvusConfig.chunks_collection,
                filter=f'item_name == "{safe}"',
                output_fields=["title", "content", "content_type", "author", "part", "item_name"],
                limit=500,
            )
    except Exception as e:
        logger.error(f"查询书籍切片失败: {e}")
        raise HTTPException(status_code=500, detail="知识库查询失败，请稍后重试")
    res.sort(key=lambda r: (r.get("part") or 0))
    sections = []
    for idx, row in enumerate(res, start=1):
        content = _clean_text(row.get("content", ""))
        sections.append({
            "index": idx,
            "title": _clean_text(row.get("title", "无标题")),
            "content_type": row.get("content_type", "书籍简介"),
            "content": content,
            "preview": content[:80] + ("..." if len(content) > 80 else ""),
        })
    return {"book_name": book_name, "sections": sections}


class TTSRequest(BaseModel):
    text: str = Field(..., description="要朗读的文本")
    voice: str = Field("zh-CN-XiaoxiaoNeural", description="发音人 id")
    rate: int = Field(0, description="语速 -100~+100")
    pitch: int = Field(0, description="音调 -50~+50")
    volume: int = Field(0, description="音量 -100~+100")


CUSTOM_VOICE_PREFIX = "custom:"


@app.post("/api/books/{book_name}/tts")
def tts_book(book_name: str, req: TTSRequest = Body(...)):
    """把文本合成为语音（MP3/WAV），供前端 <audio> 播放。

    voice 参数两种取值：
    - 系统音色 id（如 zh-CN-XiaoxiaoNeural）→ edge-tts 合成
    - "custom:音色名" → 用 DashScope 复刻的自定义音色合成（rate/pitch 参数不生效）
    """
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="朗读文本不能为空")
    try:
        if req.voice.startswith(CUSTOM_VOICE_PREFIX):
            voice_name = req.voice[len(CUSTOM_VOICE_PREFIX):]
            voice = get_tts_voice(voice_name)
            if not voice:
                raise HTTPException(status_code=404, detail=f"自定义音色「{voice_name}」不存在，请先上传声音")
            audio = synthesize_clone(text=req.text, voice_id=voice["voice_id"])
            media_type = "audio/wav"
        else:
            audio = synthesize(
                text=req.text,
                voice=req.voice,
                rate=req.rate,
                pitch=req.pitch,
                volume=req.volume,
            )
            media_type = "audio/mpeg"
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TTS 合成失败: {e}")
        raise HTTPException(status_code=500, detail=f"语音合成失败: {str(e)[:100]}")
    return Response(content=audio, media_type=media_type)


@app.get("/api/tts/voices")
def tts_voices():
    """系统发音人列表（edge-tts）"""
    return {"items": get_voices()}


@app.post("/api/tts/upload-voice")
async def upload_voice(file: UploadFile = File(...), name: str = Form(...)):
    """上传一段 mp3 参考音频，复刻成自定义音色（DashScope 声音复刻）。

    音频要求：10~60 秒、清晰无背景噪音、连续朗读的普通话/中文样本。
    复刻成功后音色持久化保存，之后可用 voice="custom:名称" 朗读任意文本。
    """
    name = (name or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="请填写音色名称")
    if len(name) > 30:
        raise HTTPException(status_code=400, detail="音色名称过长（最多 30 字）")
    if get_tts_voice(name):
        raise HTTPException(status_code=400, detail=f"音色「{name}」已存在，请换个名称")

    filename = (file.filename or "").lower()
    if not (filename.endswith(".mp3") or filename.endswith(".wav")):
        raise HTTPException(status_code=400, detail="仅支持 mp3 / wav 音频文件")
    audio_bytes = await file.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="音频文件为空")
    if len(audio_bytes) > 30 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="音频文件过大（上限 30MB）")

    try:
        mime = "audio/wav" if filename.endswith(".wav") else "audio/mpeg"
        voice_id = create_cloned_voice(name=name, audio_bytes=audio_bytes, mime=mime)
    except Exception as e:
        logger.error(f"声音复刻失败: {e}")
        raise HTTPException(status_code=502, detail=f"声音复刻失败（请确认音频清晰、10~60 秒）: {str(e)[:120]}")

    from atguigu.config.config import TtsConfig
    save_tts_voice(name=name, voice_id=voice_id, target_model=TtsConfig.clone_model)
    return {"name": name, "voice_id": voice_id, "voice": f"{CUSTOM_VOICE_PREFIX}{name}"}


@app.get("/api/tts/custom-voices")
def tts_custom_voices():
    """用户自定义音色列表（上传 mp3 复刻所得）"""
    voices = [_clean_mongo_record(v) for v in list_tts_voices()]
    for v in voices:
        v["voice"] = f"{CUSTOM_VOICE_PREFIX}{v['name']}"
    return {"items": voices}


@app.get("/api/import-records")
def import_records():
    """导入记录（持久化，刷新不丢）"""
    records = list_import_records(limit=50)
    return {"items": [_clean_mongo_record(r) for r in records]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)
