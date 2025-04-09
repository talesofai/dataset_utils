"""
MongoDB 连接工具类，提供基础的 MongoDB 连接功能
"""

import pymongo
from urllib.parse import quote_plus
from dataset_utils.utils.logger import setup_logger
from dataset_utils.config import LOG_LEVEL_INT

class MongoDBClient:
    """MongoDB 连接工具类"""

    def __init__(
        self,
        mongo_uri: str = "mongodb://localhost:27017/",
        log_level: int = LOG_LEVEL_INT
    ):
        """
        初始化 MongoDB 客户端

        Args:
            mongo_uri: MongoDB 连接 URI (默认本地无密码连接)
            log_level: 日志级别
        """
        # 配置日志
        self.logger = setup_logger(__name__, log_level)

        # 数据库配置
        self.mongo_uri = mongo_uri # self._quote_url(mongo_uri)
        self.mongo_client = None

        # 连接 MongoDB
        self._connect_mongodb()

    def _quote_url(self, url: str) -> str:
        """对 URL 进行 URL 编码"""
        return quote_plus(url)

    def _connect_mongodb(self) -> None:
        """连接到 MongoDB 数据库"""
        self.logger.info(f"正在连接 MongoDB: {self.mongo_uri}")
        self.mongo_client = pymongo.MongoClient(
            self.mongo_uri,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000
        )

        # 测试连接
        self.mongo_client.admin.command('ping')
        self.logger.info("MongoDB 连接成功")

    def get_database(self, db_name: str):
        """获取数据库对象"""
        return self.mongo_client[db_name]

    def get_collection(self, db_name: str, collection_name: str):
        """获取集合对象"""
        return self.mongo_client[db_name][collection_name]

    def close(self) -> None:
        """关闭 MongoDB 连接"""
        if self.mongo_client:
            self.mongo_client.close()
            self.logger.info("MongoDB 连接已关闭")