import json
import os

from bson import json_util
from pymongo import MongoClient

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "data")

client = MongoClient("mongodb://127.0.0.1:27017/")
db = client["library"]


def load_json_array(path):
        with open(path, "r", encoding="utf-8") as f:
        return json_util.loads(f.read())


def import_books():
    """图书：insert_one 录入第一条，insert_many 批量录入其余"""
    books = load_json_array(os.path.join(DATA_DIR, "books.txt"))
    print(f"[books] 数据文件共 {len(books)} 条")

    first, rest = books[0], books[1:]
    # 1) insertOne 单独录入第一条图书文档
    result = db.books.insert_one(first)
    print(f"[books] insert_one 返回 _id = {result.inserted_id}，acknowledged = {result.acknowledged}")

    # 2) insertMany 批量录入其余数据
    result = db.books.insert_many(rest)
    print(f"[books] insert_many 批量录入 {len(result.inserted_ids)} 条")
    print(f"[books] 集合当前文档总数 = {db.books.count_documents({})}")


def import_readers():
    """读者：insert_many 批量录入"""
    readers = load_json_array(os.path.join(DATA_DIR, "readers.txt"))
    print(f"\n[readers] 数据文件共 {len(readers)} 条")
    result = db.readers.insert_many(readers)
    print(f"[readers] insert_many 批量录入 {len(result.inserted_ids)} 条")
    print(f"[readers] 集合当前文档总数 = {db.readers.count_documents({})}")


def import_borrow_logs():
    """借阅流水（时间序列集合）：insert_many 批量录入"""
    logs = load_json_array(os.path.join(DATA_DIR, "borrow_logs.txt"))
    print(f"\n[borrow_logs] 数据文件共 {len(logs)} 条")
    result = db.borrow_logs.insert_many(logs)
    print(f"[borrow_logs] insert_many 批量录入 {len(result.inserted_ids)} 条")
    print(f"[borrow_logs] 集合当前文档总数 = {db.borrow_logs.count_documents({})}")


if __name__ == "__main__":
    import_books()
    import_readers()
    import_borrow_logs()
    print("\n===== 各集合文档数量核对 =====")
    for name in ["books", "readers", "borrow_logs", "book_logs", "category_stats"]:
        print(f"  {name:<16} -> {db[name].count_documents({})} 条")
    print(f"  视图 book_in_stock    -> {db['book_in_stock'].count_documents({})} 条")
    client.close()
    print("\n数据导入完成，连接已关闭。")
