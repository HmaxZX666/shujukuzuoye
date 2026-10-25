import os

from bson import json_util
from pymongo import MongoClient

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "data")

client = MongoClient("mongodb://127.0.0.1:27017/")
db = client["library"]

# 1) collMod 放宽过期时间：63072000（2年）-> 630720000（20年）
before = db.command("collMod", "borrow_logs", expireAfterSeconds=630720000)
print("[collMod] 调整结果:", before)

# 2) 删除被 TTL 部分清理的时间序列集合（连同 system.buckets 一起删除）
db.drop_collection("borrow_logs")
print("[drop] 已删除原 borrow_logs 集合")

# 3) 重建时间序列集合（保持 timeField=borrow_date，granularity=hours，过期时间放宽后）
db.create_collection(
    "borrow_logs",
    timeseries={"timeField": "borrow_date", "granularity": "hours"},
    expireAfterSeconds=630720000,
)
print("[create] 已重建时间序列集合 borrow_logs")

# 4) 从原始数据集完整导入 66 条借阅流水
with open(os.path.join(DATA_DIR, "borrow_logs.txt"), "r", encoding="utf-8") as f:
    logs = json_util.loads(f.read())
result = db.borrow_logs.insert_many(logs)
print(f"[import] 重新导入 {len(result.inserted_ids)} 条借阅流水")

# 5) 验证
print(f"[verify] borrow_logs 文档总数 = {db.borrow_logs.count_documents({})}")
print("\n按年份分布:")
for d in db.borrow_logs.aggregate([
    {"$group": {"_id": {"$year": "$borrow_date"}, "n": {"$sum": 1}}},
    {"$sort": {"_id": 1}},
]):
    print(f"  {d['_id']} 年 -> {d['n']} 条")

client.close()
print("\n数据恢复完成。")
