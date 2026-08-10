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
#     "ts": 123
# }

def get_history_list(session_id, limit=10):
    mongo_tool = get_mongo_tool()
    result = mongo_tool.find({"session_id": session_id}).sort("ts", -1).limit(limit)
    return list(result)

def clear_history_list(session_id):
    mongo_tool = get_mongo_tool()
    mongo_tool.delete_many({"session_id": session_id})


def add_or_update_history(session_id, role, text, rewritten_query="", item_names=[], ts=None,message_id=None):
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

