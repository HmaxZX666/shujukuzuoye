from datetime import datetime

from mongodb_connect import get_db

db = get_db()
COLL = db["borrow_logs"]


# ---------- 借阅登记 ----------
def borrow_book(reader_card, book_isbn):
    """登记一条借阅记录（insert_one），状态为「借出」"""
    record = {
        "borrow_date": datetime.now(),
        "reader_card": reader_card,
        "book_isbn": book_isbn,
        "status": "借出",
    }
    result = COLL.insert_one(record)
    return result.inserted_id


# ---------- 归还处理 ----------
def return_book(reader_card, book_isbn):
    """归还处理：
    说明：borrow_logs 为时间序列集合且未定义 metaField 时，MongoDB 不允许对其执行
          update 操作（错误码 72: Cannot perform an update on a time-series collection
          that does not have a metaField）。因此对借阅流水采用
          「删除借出记录 + 插入已归还记录」实现状态变更的等价效果；
          同时使用 update_many 对 books（普通集合）执行库存 +1（归还图书回库），
          以演示 update_many 的常规用法。
    """
    # (1) 归还图书回库：update_many 更新 books 集合库存 +1
    db["books"].update_many({"isbn": book_isbn}, {"$inc": {"stock": 1}})

    # (2) 借阅流水状态变更（时间序列集合兼容实现：删除 + 插入）
    deleted = COLL.delete_many(
        {"reader_card": reader_card, "book_isbn": book_isbn, "status": "借出"}
    ).deleted_count
    if deleted > 0:
        now = datetime.now()
        COLL.insert_one({
            "borrow_date": now,
            "return_date": now,
            "reader_card": reader_card,
            "book_isbn": book_isbn,
            "status": "已归还",
        })
    return deleted, deleted


# ---------- 查询 ----------
def find_overdue():
    """查询逾期未还记录"""
    return list(COLL.find({"status": "逾期"}))


def find_borrowing():
    """查询当前借出记录"""
    return list(COLL.find({"status": "借出"}))


def list_borrows(limit=10):
    """查看最近借阅记录"""
    return list(COLL.find().sort("borrow_date", -1).limit(limit))


if __name__ == "__main__":
    # 模块自检（只读部分）
    print("borrow_manager 模块自检：")
    print("  当前借出记录:", len(find_borrowing()), "条")
    print("  逾期记录:", len(find_overdue()), "条")
    print("  最近借阅:")
    for b in list_borrows(3):
        print("   ", b["reader_card"], b["book_isbn"], b["status"])
