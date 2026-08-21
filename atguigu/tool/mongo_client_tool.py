import time

from pymongo import MongoClient
from atguigu.config.config import MongoConfig


mongo_client = None
def get_mongo_client():
    global mongo_client
    if not mongo_client:
        mongo_client = MongoClient(MongoConfig.mongo_url)
    return mongo_client


mongo_tool = None
def get_mongo_tool():
    global mongo_tool
    if mongo_tool is None:
        mongo_db = get_mongo_client()[MongoConfig.mongo_db_name]
        mongo_tool = mongo_db['chat']
        mongo_tool.create_index([('session_id', 1),("ts",-1)])
    return mongo_tool



#
# {
#     "session_id": "",
#     "role": "",
#     "text": "",
#     "rewritten_query": "",
#     "item_names": [],
#     "image_urls": [],
#     "ts": 123
# }

def get_history_list(session_id, limit=10):
    mongo_tool = get_mongo_tool()
    result = mongo_tool.find({"session_id": session_id}).sort("ts", -1).limit(limit)
    return list(result)

def clear_history_list(session_id):
    mongo_tool = get_mongo_tool()
    mongo_tool.delete_many({"session_id": session_id})


def add_or_update_history(session_id, role, text, rewritten_query="", item_names=[], ts=None, message_id=None, image_urls=None):
    mongo_tool = get_mongo_tool()
    if message_id:
        mongo_tool.update_one(
            {"_id": message_id},
            {
                "$set": {
                    "session_id": session_id,
                    "role": role,
                    "text": text,
                    "rewritten_query": rewritten_query,
                    "item_names": item_names,
                    "image_urls": image_urls or [],
                    "ts": ts or int(time.time())
                }
            }
        )
        return message_id
    else:
        result = mongo_tool.insert_one({
            "session_id": session_id,
            "role": role,
            "text": text,
            "rewritten_query": rewritten_query,
            "item_names": item_names,
            "image_urls": image_urls or [],
            "ts": ts or int(time.time())
        })
        return result.inserted_id


def update_history_item_names(ids,item_names,rewritten_query):
    mongo_tool = get_mongo_tool()
    mongo_tool.update_many(
        {"_id": {"$in": ids}},
        {
            "$set": {
                "item_names": item_names,
                "rewritten_query": rewritten_query
            }
        }
    )


# ==================== 书库与导入记录持久化（library 模块使用） ====================

def get_books_collection():
    """书库集合：每本已导入的书籍一条记录（book_name 唯一）"""
    mongo_db = get_mongo_client()[MongoConfig.mongo_db_name]
    coll = mongo_db['books']
    coll.create_index([('book_name', 1)], unique=True)
    return coll


def get_import_records_collection():
    """导入记录集合：每次上传/导入一条记录"""
    mongo_db = get_mongo_client()[MongoConfig.mongo_db_name]
    coll = mongo_db['import_records']
    coll.create_index([('task_id', 1)])
    return coll


def upsert_book(book_info):
    """登记/更新一本书（按 book_name upsert）。book_info 至少含 book_name。"""
    coll = get_books_collection()
    book_info["import_time"] = int(time.time())
    coll.update_one(
        {"book_name": book_info.get("book_name", "")},
        {"$set": book_info},
        upsert=True,
    )


def list_books():
    """返回书库全部书籍，按导入时间倒序"""
    return list(get_books_collection().find().sort("import_time", -1))


def get_book(book_name):
    return get_books_collection().find_one({"book_name": book_name})


def add_import_record(record):
    """新增一条导入记录：task_id / file_name / book_names / status"""
    coll = get_import_records_collection()
    record["ts"] = int(time.time())
    coll.insert_one(record)


def update_import_record(task_id, status, book_names=None):
    """更新导入记录状态：processing / completed / failed"""
    coll = get_import_records_collection()
    update = {"status": status, "update_time": int(time.time())}
    if book_names is not None:
        update["book_names"] = book_names
    coll.update_one({"task_id": task_id}, {"$set": update})


def list_import_records(limit=50):
    """返回最近的导入记录，按时间倒序"""
    return list(get_import_records_collection().find().sort("ts", -1).limit(limit))


# ==================== 自定义音色持久化（TTS 声音复刻） ====================

def get_tts_voices_collection():
    """自定义音色集合：用户上传 mp3 复刻出的音色（name 唯一）"""
    mongo_db = get_mongo_client()[MongoConfig.mongo_db_name]
    coll = mongo_db['tts_voices']
    coll.create_index([('name', 1)], unique=True)
    return coll


def save_tts_voice(name, voice_id, target_model=""):
    """保存/更新一个自定义音色（按 name upsert）"""
    coll = get_tts_voices_collection()
    coll.update_one(
        {"name": name},
        {"$set": {
            "voice_id": voice_id,
            "target_model": target_model,
            "created_at": int(time.time()),
        }},
        upsert=True,
    )


def get_tts_voice(name):
    return get_tts_voices_collection().find_one({"name": name})


def list_tts_voices():
    """返回全部自定义音色，按创建时间倒序"""
    return list(get_tts_voices_collection().find().sort("created_at", -1))

if __name__ == "__main__":

    # 模拟会话历史
    session_id = "test_001"
    add_or_update_history(session_id, "user", "咨询下烫金机。")
    add_or_update_history(session_id, "assistant", "您好。请问是哪个型号")
    add_or_update_history(session_id, "user", "hak180")
    add_or_update_history(session_id, "assistant", "具体有什么问题呢？")

    # 初始化图状态
    init_state = {
        "session_id": "test_001",
        "original_query": "咋用？"
    }

