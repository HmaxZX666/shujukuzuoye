from mongodb_connect import get_db

db = get_db()
COLL = db["books"]


# ---------- 查询 ----------
def query_by_isbn(isbn):
    """按 ISBN 精确查找"""
    return COLL.find_one({"isbn": isbn})


def query_by_keyword(keyword):
    """按书名或作者模糊检索（$regex）"""
    return list(COLL.find({
        "$or": [
            {"title": {"$regex": keyword}},
            {"author": {"$regex": keyword}},
        ]
    }))


def query_combined(category=None, min_price=None, max_price=None, min_rating=None):
    """组合条件检索：类别 + 价格范围 + 评分下限"""
    cond = {}
    if category:
        cond["category"] = category
    if min_price is not None or max_price is not None:
        price = {}
        if min_price is not None:
            price["$gte"] = min_price
        if max_price is not None:
            price["$lte"] = max_price
        cond["price"] = price
    if min_rating is not None:
        cond["rating"] = {"$gte": min_rating}
    return list(COLL.find(cond))


def rating_ranking(limit=5):
    """按评分降序排行，取前 limit 本"""
    return list(COLL.find().sort("rating", -1).limit(limit))


def list_books(limit=10):
    """列出图书（分页查看）"""
    return list(COLL.find().limit(limit))


# ---------- 新增 ----------
def add_book(book):
    """新增一本图书（insert_one）"""
    result = COLL.insert_one(book)
    return result.inserted_id


def add_books(books):
    """批量新增图书（insert_many）"""
    if not books:
        return 0
    result = COLL.insert_many(books)
    return len(result.inserted_ids)


# ---------- 更新 ----------
def update_stock(isbn, delta):
    """按 ISBN 调整库存（update_one + $inc），delta 可为正负"""
    result = COLL.update_one({"isbn": isbn}, {"$inc": {"stock": delta}})
    return result.matched_count, result.modified_count


# ---------- 删除 ----------
def delete_book(isbn):
    """按 ISBN 删除图书（delete_one）"""
    result = COLL.delete_one({"isbn": isbn})
    return result.deleted_count


def delete_books_by_category(category):
    """按类别批量删除图书（delete_many）"""
    result = COLL.delete_many({"category": category})
    return result.deleted_count


if __name__ == "__main__":
    # 模块自检
    print("book_manager 模块自检：")
    print("  ISBN 9787115428028 ->", query_by_isbn("9787115428028")["title"])
    print("  关键词 '算法' 命中:", len(query_by_keyword("算法")), "本")
    print("  计算机类价格>80:", len(query_combined(category="计算机", min_price=80)), "本")
    print("  评分排行前3:")
    for b in rating_ranking(3):
        print("   ", b["title"], b["rating"])
