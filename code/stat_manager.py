from mongodb_connect import get_db

db = get_db()


def category_stats():
    """分类统计：按类别分组，统计库存总量、平均价格、图书数量，按库存总量降序排列"""
    pipeline = [
        {"$group": {
            "_id": "$category",
            "stock_total": {"$sum": "$stock"},
            "avg_price": {"$avg": "$price"},
            "book_count": {"$sum": 1},
        }},
        {"$sort": {"stock_total": -1}},
        {"$project": {
            "_id": 0,
            "category": "$_id",
            "stock_total": 1,
            "avg_price": {"$round": ["$avg_price", 2]},
            "book_count": 1,
        }},
    ]
    return list(db["books"].aggregate(pipeline))


def borrow_trend():
    """借阅趋势：按年份分组统计借阅量，格式化后输出（如"2024年"）"""
    pipeline = [
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y年", "date": "$borrow_date"}},
            "borrow_count": {"$sum": 1},
        }},
        {"$sort": {"_id": 1}},
    ]
    return list(db["borrow_logs"].aggregate(pipeline))


def bestseller(limit=5):
    """畅销榜：取借阅次数最多的图书"""
    pipeline = [
        {"$sort": {"borrow_count": -1}},
        {"$limit": limit},
        {"$project": {"_id": 0, "title": 1, "borrow_count": 1, "price": 1, "category": 1}},
    ]
    return list(db["books"].aggregate(pipeline))


if __name__ == "__main__":
    # 模块自检
    print("stat_manager 模块自检：")
    print("  分类统计:")
    for s in category_stats():
        print("   ", s["category"], "| 库存总量", s["stock_total"], "| 平均价格", s["avg_price"], "| 图书数", s["book_count"])
    print("  借阅趋势:")
    for t in borrow_trend():
        print("   ", t["_id"], t["borrow_count"], "次")
    print("  畅销榜:")
    for b in bestseller(3):
        print("   ", b["title"], b["borrow_count"], "次")
