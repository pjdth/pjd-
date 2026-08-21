# atguigu/tool/tts_tool.py
"""文字转语音工具。

两套引擎：
1. edge-tts（微软免费神经网络语音，无需 API Key）：系统音色，支持语速/音调/音量
2. DashScope 声音复刻（qwen-voice-enrollment + qwen3-tts-vc）：
   用户上传 mp3 参考音频 → 创建自定义音色 → 用该音色朗读文本

synthesize() 返回 MP3 音频字节，可通过 HTTP 直接返回给前端 <audio> 播放。
"""
import asyncio
import base64
import re
import time

import edge_tts
import requests

from atguigu.config.config import TtsConfig
from atguigu.tool.logger import logger

# 可用的中文发音人列表（id 为 edge-tts 语音名，name 为前端展示的中文名）
TTS_VOICES = [
    {"id": "zh-CN-XiaoxiaoNeural", "name": "晓晓（女声·温柔）"},
    {"id": "zh-CN-XiaoyiNeural", "name": "晓伊（女声·甜美）"},
    {"id": "zh-CN-XiaoxuanNeural", "name": "晓萱（女声·自然）"},
    {"id": "zh-CN-XiaomoNeural", "name": "晓墨（女声·亲切）"},
    {"id": "zh-CN-XiaohanNeural", "name": "晓涵（女声·温和）"},
    {"id": "zh-CN-YunxiNeural", "name": "云希（男声·阳光）"},
    {"id": "zh-CN-YunjianNeural", "name": "云健（男声·沉稳）"},
    {"id": "zh-CN-YunyangNeural", "name": "云扬（男声·新闻播报）"},
    {"id": "zh-CN-YunxiaNeural", "name": "云夏（男声·少年）"},
    {"id": "zh-CN-YunfengNeural", "name": "云枫（男声·浑厚）"},
]


def get_voices():
    """返回可用发音人列表（用于前端下拉选择）"""
    return TTS_VOICES


def _normalize_percent(value, name="rate"):
    """把 -100~+100 的数字转成 edge-tts 的 '±N%' 格式（rate/volume 用）"""
    value = max(-100, min(100, int(value)))
    if value >= 0:
        return f"+{value}%"
    return f"{value}%"


def _normalize_pitch(value):
    """把 -50~+50 的数字转成 edge-tts 的 '±NHz' 格式（pitch 用）"""
    value = max(-50, min(50, int(value)))
    if value >= 0:
        return f"+{value}Hz"
    return f"{value}Hz"


async def _synthesize_async(text, voice, rate, pitch, volume):
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=rate,
        pitch=pitch,
        volume=volume,
    )
    audio = bytearray()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio.extend(chunk["data"])
    return bytes(audio)


def synthesize(text, voice="zh-CN-XiaoxiaoNeural", rate=0, pitch=0, volume=0):
    """把文本合成为语音。

    Args:
        text: 要朗读的文本
        voice: 发音人 id（见 TTS_VOICES）
        rate: 语速，-100 ~ +100（0 为正常）
        pitch: 音调，-50 ~ +50（0 为正常）
        volume: 音量，-100 ~ +100（0 为正常）
    Returns:
        bytes: MP3 音频数据；失败时抛异常
    """
    if not text or not text.strip():
        raise ValueError("text 为空，无法合成语音")
    rate_s = _normalize_percent(rate, "rate")
    pitch_s = _normalize_pitch(pitch)
    volume_s = _normalize_percent(volume, "volume")
    logger.info(f"TTS 合成: voice={voice} rate={rate_s} pitch={pitch_s} volume={volume_s} 文本长度={len(text)}")
    return asyncio.run(_synthesize_async(text, voice, rate_s, pitch_s, volume_s))


# ==================== DashScope 声音复刻（上传 mp3 创建自定义音色） ====================

def create_cloned_voice(name: str, audio_bytes: bytes, mime: str = "audio/mpeg") -> str:
    """声音复刻：上传一段参考音频，创建自定义音色，返回 voice_id。

    Args:
        name: 音色名称（preferred_name，用户自定义标识）
        audio_bytes: 参考音频（mp3/wav 等）的原始字节
        mime: 音频 MIME 类型，默认 audio/mpeg（mp3）
    Returns:
        str: voice_id，后续合成时作为 voice 参数使用
    """
    if not audio_bytes:
        raise ValueError("参考音频为空")
    # preferred_name 只允许字母/数字/下划线（中文等字符会触发 API 400 InvalidParameter），
    # 这里把用户输入的名称清洗成合法 ASCII；全被剔光时退回时间戳标识（最终 voice_id 仍唯一）。
    preferred_name = re.sub(r"[^A-Za-z0-9_]", "", (name or ""))[:20] or f"v{int(time.time())}"
    data_uri = f"data:{mime};base64,{base64.b64encode(audio_bytes).decode()}"
    url = TtsConfig.dashscope_base_url + "/services/audio/tts/customization"
    payload = {
        "model": "qwen-voice-enrollment",
        "input": {
            "action": "create",
            "target_model": TtsConfig.clone_model,
            "preferred_name": preferred_name,
            "audio": {"data": data_uri},
        },
    }
    resp = requests.post(
        url,
        headers={"Authorization": f"Bearer {TtsConfig.api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=180,
    )
    logger.info(f"声音复刻 create_voice status={resp.status_code} preferred_name={preferred_name}")
    if resp.status_code != 200:
        raise RuntimeError(f"创建音色失败: HTTP {resp.status_code} {resp.text[:200]}")
    voice_id = resp.json().get("output", {}).get("voice")
    if not voice_id:
        raise RuntimeError(f"创建音色失败: 响应中无 voice_id {resp.text[:200]}")
    logger.info(f"声音复刻成功: name={name} voice_id={voice_id}")
    return voice_id


def synthesize_clone(text: str, voice_id: str) -> bytes:
    """用复刻音色合成语音（DashScope qwen3-tts-vc），返回音频字节（wav）。

    Args:
        text: 要朗读的文本
        voice_id: create_cloned_voice 返回的复刻音色 id
    Returns:
        bytes: wav 音频数据
    """
    if not text or not text.strip():
        raise ValueError("text 为空，无法合成语音")
    if not voice_id:
        raise ValueError("voice_id 为空，无法使用复刻音色合成")
    url = TtsConfig.dashscope_base_url + "/services/aigc/multimodal-generation/generation"
    payload = {
        "model": TtsConfig.clone_model,
        "input": {"text": text, "voice": voice_id},
    }
    resp = requests.post(
        url,
        headers={"Authorization": f"Bearer {TtsConfig.api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=300,
    )
    logger.info(f"复刻音色合成 status={resp.status_code} 文本长度={len(text)}")
    if resp.status_code != 200:
        raise RuntimeError(f"复刻音色合成失败: HTTP {resp.status_code} {resp.text[:200]}")
    audio_url = resp.json().get("output", {}).get("audio", {}).get("url")
    if not audio_url:
        raise RuntimeError(f"复刻音色合成失败: 响应中无音频 URL {resp.text[:200]}")
    audio_resp = requests.get(audio_url, timeout=180)
    audio_resp.raise_for_status()
    return audio_resp.content


if __name__ == "__main__":
    audio = synthesize("你好，欢迎使用听书书库。这是一段文字转语音测试。", voice="zh-CN-XiaoxiaoNeural", rate=10, pitch=0)
    print(f"合成成功，音频大小: {len(audio)} 字节")
    with open("tts_test.mp3", "wb") as f:
        f.write(audio)
    print("已写入 tts_test.mp3")
