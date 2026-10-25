from urllib.parse import quote_plus

from pymongo import MongoClient

# 连接参数统一定义（使用任务四创建的有读写权限的账号 libWriter）
HOST = "127.0.0.1"
PORT = 27017
DATABASE = "library"
USERNAME = "libWriter"
PASSWORD = "LibWriter@123"
AUTH_SOURCE = "library"

# 连接 URI（启用访问控制后的认证连接；用户名/密码按 RFC 3986 进行 URL 编码）
CONN_URI = (
    f"mongodb://{quote_plus(USERNAME)}:{quote_plus(PASSWORD)}@{HOST}:{PORT}/{DATABASE}"
    f"?authSource={AUTH_SOURCE}"
)


def get_client():
    """建立 MongoClient 连接"""
    return MongoClient(CONN_URI)


def get_db():
    """获取业务数据库对象 library"""
    client = get_client()
    return client[DATABASE]


if __name__ == "__main__":
    # 自检：验证连接是否成功
    client = get_client()
    try:
        client.admin.command("ping")
        db = client[DATABASE]
        print("MongoDB 连接成功，数据库:", DATABASE)
        print("各集合文档总数:")
        for name in ["books", "readers", "borrow_logs", "category_stats"]:
            print(f"  {name:<14} -> {db[name].count_documents({})} 条")
    finally:
        client.close()
        print("连接已关闭。")
