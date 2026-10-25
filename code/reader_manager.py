from mongodb_connect import get_db

db = get_db()
COLL = db["readers"]


# ---------- 查询 ----------
def find_reader(card_no):
    """按借阅证号查找读者"""
    return COLL.find_one({"card_no": card_no})


def list_readers(limit=10):
    """列出读者"""
    return list(COLL.find().limit(limit))


def count_readers():
    """读者总数"""
    return COLL.count_documents({})


# ---------- 新增 ----------
def add_reader(reader):
    """新增读者"""
    result = COLL.insert_one(reader)
    return result.inserted_id


# ---------- 统计 ----------
def college_stats():
    """按学院统计读者人数（distinct + count_documents）"""
    colleges = COLL.distinct("college")
    stats = []
    for college in colleges:
        stats.append({
            "college": college,
            "count": COLL.count_documents({"college": college}),
        })
    stats.sort(key=lambda x: x["count"], reverse=True)
    return stats


def level_distribution():
    """借阅等级分布（distinct + count_documents）"""
    levels = COLL.distinct("level")
    dist = []
    for level in levels:
        dist.append({
            "level": level,
            "count": COLL.count_documents({"level": level}),
        })
    dist.sort(key=lambda x: x["count"], reverse=True)
    return dist


if __name__ == "__main__":
    # 模块自检
    print("reader_manager 模块自检：")
    print("  读者总数:", count_readers())
    print("  学院统计:")
    for s in college_stats():
        print("   ", s["college"], s["count"], "人")
    print("  等级分布:")
    for d in level_distribution():
        print("   ", d["level"], d["count"], "人")
