from datetime import datetime

from mongodb_connect import get_client, get_db, CONN_URI
import book_manager as bm
import reader_manager as rm
import borrow_manager as brm
import stat_manager as sm


def show_connection_status(client):
    """打印数据库连接状态与各集合文档总数"""
    db = client["library"]
    print("=" * 58)
    print(" 图书情报检索与统计平台（PyMongo 版）")
    print("=" * 58)
    print(f" 连接地址 : {CONN_URI.split('@')[-1]}")
    print(f" 数据库   : library")
    try:
        client.admin.command("ping")
        print(" 连接状态 : 已连接 MongoDB（OK）")
    except Exception as e:
        print(" 连接状态 : 连接失败 ->", e)
        return False
    print(" 集合文档总数：")
    for name in ["books", "readers", "borrow_logs", "category_stats"]:
        print(f"   {name:<14} -> {db[name].count_documents({})} 条")
    return True


def show_menu():
    print("\n" + "-" * 58)
    print(" 功能菜单：")
    print("  1. 图书检索（书名/作者关键词）")
    print("  2. 图书组合条件检索（类别+价格区间）")
    print("  3. 图书评分排行（前 N 本）")
    print("  4. 新增图书（insert_one）")
    print("  5. 批量新增图书（insert_many）")
    print("  6. 更新图书库存（$inc）")
    print("  7. 删除图书（按 ISBN）")
    print("  8. 读者信息查询")
    print("  9. 读者统计（学院分布/等级分布）")
    print(" 10. 借阅登记")
    print(" 11. 归还处理")
    print(" 12. 逾期记录查询")
    print(" 13. 分类统计报表（聚合管道）")
    print(" 14. 借阅趋势分析（按年份）")
    print(" 15. 图书畅销榜（借阅次数 TOP N）")
    print("  0. 退出程序")
    print("-" * 58)


# ---------- 各功能实现 ----------
def f1_search_book():
    kw = input("请输入书名/作者关键词：").strip()
    if not kw:
        print("  [提示] 关键词不能为空")
        return
    books = bm.query_by_keyword(kw)
    if not books:
        print("  [提示] 未找到符合条件的图书")
        return
    print(f"  命中 {len(books)} 本：")
    for b in books:
        print(f"   - {b['title']} | {b['author']} | ￥{b['price']} | 库存 {b['stock']}")


def f2_combined_search():
    category = input("请输入类别（回车跳过）：").strip()
    min_price = input("最低价格（回车跳过）：").strip()
    max_price = input("最高价格（回车跳过）：").strip()
    min_rating = input("最低评分（回车跳过）：").strip()
    cond = {
        "category": category or None,
        "min_price": float(min_price) if min_price else None,
        "max_price": float(max_price) if max_price else None,
        "min_rating": float(min_rating) if min_rating else None,
    }
    books = bm.query_combined(**cond)
    if not books:
        print("  [提示] 未找到符合条件的图书")
        return
    print(f"  命中 {len(books)} 本：")
    for b in books:
        print(f"   - [{b['category']}] {b['title']} | ￥{b['price']} | 评分 {b['rating']}")


def f3_rating_ranking():
    n = input("请输入排行数量（默认 5）：").strip()
    limit = int(n) if n.isdigit() and int(n) > 0 else 5
    books = bm.rating_ranking(limit)
    if not books:
        print("  [提示] 暂无图书数据")
        return
    print(f"  评分排行前 {len(books)}：")
    for i, b in enumerate(books, 1):
        print(f"   {i}. {b['title']} | 评分 {b['rating']} | 借阅 {b['borrow_count']} 次")


def f4_add_book():
    print("  请输入图书信息：")
    isbn = input("  ISBN：").strip()
    title = input("  书名：").strip()
    author = input("  作者：").strip()
    publisher = input("  出版社：").strip()
    category = input("  类别：").strip()
    price = float(input("  价格：").strip() or 0)
    stock = int(input("  库存：").strip() or 0)
    rating = float(input("  评分：").strip() or 0)
    book = {
        "isbn": isbn, "title": title, "author": author, "publisher": publisher,
        "category": category, "price": price, "stock": stock, "rating": rating,
        "tags": [], "publish_date": datetime.now(), "borrow_count": 0,
    }
    new_id = bm.add_book(book)
    print(f"  [成功] 已新增图书 1 本，_id = {new_id}")


def f5_add_books():
    print("  演示 insert_many：批量新增 2 本示例图书")
    books = [
        {"isbn": "DEMO000001", "title": "NoSQL数据库技术与应用（演示）", "author": "演示作者",
         "publisher": "示例出版社", "category": "计算机", "price": 59.0, "stock": 10,
         "rating": 4.0, "tags": ["NoSQL", "数据库"], "publish_date": datetime.now(), "borrow_count": 0},
        {"isbn": "DEMO000002", "title": "MongoDB 实战（演示）", "author": "演示作者",
         "publisher": "示例出版社", "category": "计算机", "price": 69.0, "stock": 8,
         "rating": 4.2, "tags": ["MongoDB", "数据库"], "publish_date": datetime.now(), "borrow_count": 0},
    ]
    n = bm.add_books(books)
    print(f"  [成功] 批量新增图书 {n} 本")


def f6_update_stock():
    isbn = input("请输入 ISBN：").strip()
    delta = int(input("库存调整量（正数增加，负数减少，如 -5）：").strip() or 0)
    matched, modified = bm.update_stock(isbn, delta)
    print(f"  [结果] 匹配文档 {matched} 条，实际修改 {modified} 条")


def f7_delete_book():
    isbn = input("请输入 ISBN：").strip()
    deleted = bm.delete_book(isbn)
    print(f"  [结果] 删除图书 {deleted} 本")


def f8_find_reader():
    card = input("请输入借阅证号（如 R20240001）：").strip()
    r = rm.find_reader(card)
    if not r:
        print("  [提示] 未找到该读者")
        return
    print(f"  {r['card_no']} {r['name']} | {r['college']} | 等级 {r['level']} | 邮箱 {r.get('email')}")


def f9_reader_stats():
    print("  1) 学院分布")
    for s in rm.college_stats():
        print(f"     {s['college']}: {s['count']} 人")
    print("  2) 等级分布")
    for d in rm.level_distribution():
        print(f"     {d['level']}: {d['count']} 人")


def f10_borrow():
    card = input("请输入借阅证号：").strip()
    isbn = input("请输入图书 ISBN：").strip()
    if not rm.find_reader(card):
        print("  [提示] 该读者不存在，无法借阅")
        return
    if not bm.query_by_isbn(isbn):
        print("  [提示] 该图书不存在，无法借阅")
        return
    bid = brm.borrow_book(card, isbn)
    print(f"  [成功] 借阅登记完成，流水 _id = {bid}")


def f11_return():
    card = input("请输入借阅证号：").strip()
    isbn = input("请输入图书 ISBN：").strip()
    handled, updated = brm.return_book(card, isbn)
    print(f"  [结果] 处理借出记录 {handled} 条，图书库存已回库 {updated} 本")


def f12_overdue():
    records = brm.find_overdue()
    if not records:
        print("  [提示] 当前没有逾期记录")
        return
    print(f"  逾期记录 {len(records)} 条：")
    for r in records:
        print(f"   - {r['reader_card']} 借阅 {r['book_isbn']}，状态 {r['status']}")


def f13_category_report():
    rows = sm.category_stats()
    if not rows:
        print("  [提示] 暂无统计结果")
        return
    print("  分类统计（库存总量降序）：")
    print("   {:<8} {:<10} {:<10} {:<8}".format("类别", "库存总量", "平均价格", "图书数"))
    for r in rows:
        print("   {:<8} {:<10} {:<10} {:<8}".format(
            r["category"], r["stock_total"], r["avg_price"], r["book_count"]))


def f14_trend():
    rows = sm.borrow_trend()
    if not rows:
        print("  [提示] 暂无借阅数据")
        return
    print("  借阅趋势（按年份）：")
    for r in rows:
        print(f"   - {r['_id']}: {r['borrow_count']} 次")


def f15_bestseller():
    n = input("请输入 TOP N（默认 5）：").strip()
    limit = int(n) if n.isdigit() and int(n) > 0 else 5
    rows = sm.bestseller(limit)
    if not rows:
        print("  [提示] 暂无图书数据")
        return
    print(f"  畅销榜 TOP {len(rows)}：")
    for i, b in enumerate(rows, 1):
        print(f"   {i}. {b['title']} | 借阅 {b['borrow_count']} 次 | ￥{b['price']}")


FUNCS = {
    "1": f1_search_book, "2": f2_combined_search, "3": f3_rating_ranking,
    "4": f4_add_book, "5": f5_add_books, "6": f6_update_stock, "7": f7_delete_book,
    "8": f8_find_reader, "9": f9_reader_stats, "10": f10_borrow, "11": f11_return,
    "12": f12_overdue, "13": f13_category_report, "14": f14_trend, "15": f15_bestseller,
}


def main():
    client = get_client()
    if not show_connection_status(client):
        client.close()
        return
    while True:
        show_menu()
        choice = input("请选择功能（0 退出）：").strip()
        if choice == "0":
            break
        func = FUNCS.get(choice)
        if not func:
            print("  [提示] 无效选项，请重新输入")
            continue
        func()
    client.close()
    print("\n程序已退出，数据库连接已关闭。感谢使用图书情报检索与统计平台！")


if __name__ == "__main__":
    main()
