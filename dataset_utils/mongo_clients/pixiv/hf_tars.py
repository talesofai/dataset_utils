"""
HF Tars 业务逻辑模块，用于处理 pixiv.hf_tars 集合的操作
"""

from typing import Optional, Union
from dataset_utils.utils.logger import setup_logger
from dataset_utils.mongo_clients.mongo_client import MongoDBClient
from dataset_utils.config import LOG_LEVEL_INT

class HFTarsClient:
    """Pixiv HF Tars MongoDB 客户端"""

    db_name = "pixiv"
    collection_name = "hf_tars"

    def __init__(
        self,
        mongo_client_or_uri: Union[MongoDBClient, str],
        log_level: int = LOG_LEVEL_INT
    ):
        """
        初始化 Pixiv HF Tars MongoDB 客户端

        Args:
            mongo_client_or_uri: MongoDBClient 对象或 MongoDB 连接 URI
            db_name: 数据库名称
            collection_name: 集合名称
            log_level: 日志级别
        """
        # 配置日志
        self.logger = setup_logger(__name__, log_level)

        # 设置 MongoDB 客户端
        if isinstance(mongo_client_or_uri, MongoDBClient):
            self.mongo_client = mongo_client_or_uri
            self.owns_client = False
        else:
            self.mongo_client = MongoDBClient(mongo_client_or_uri, log_level)
            self.owns_client = True

        # 获取集合
        self.collection = self.mongo_client.get_collection(self.db_name, self.collection_name)
        self.logger.info(f"已连接到集合: {self.db_name}.{self.collection_name}")

    def get_tar_urls_by_id(self, tar_id: Union[str, int]) -> Optional[str]:
        """
        根据 ID 获取 tar 文件 URL

        Args:
            tar_id: tar 文件 ID

        Returns:
            tar 文件 URL，如果不存在则返回 None
        """
        tar_id = int(tar_id)

        # 查找文档
        docs = self.collection.find({"id": tar_id})
        if not docs:
            self.logger.warning(f"未找到 ID 为 {tar_id} 的 tar 文件记录")
            return []

        # 返回 URL
        urls = [doc.get("url") for doc in docs]
        if not urls:
            self.logger.warning(f"ID 为 {tar_id} 的记录没有 URL 字段")
            return []

        return urls

    def get_tar_url_by_key(self, key: int) -> Optional[str]:
        """
        根据 key 获取 tar 文件 URL

        Args:
            key: tar 文件的 key 值

        Returns:
            tar 文件 URL，如果不存在则返回 None
        """
        # 查找文档
        doc = self.collection.find_one({"key": key})
        if not doc:
            self.logger.warning(f"未找到 key 为 {key} 的 tar 文件记录")
            return None

        # 返回 URL
        url = doc.get("url")
        if not url:
            self.logger.warning(f"key 为 {key} 的记录没有 URL 字段")
            return None

        return url

    def close(self) -> None:
        """关闭资源"""
        if self.owns_client:
            self.mongo_client.close()

    def get_tar_url_by_default_id(self, _id: Union[str, int]) -> Optional[str]:
        """
        根据 ID 获取 tar 文件 URL

        Args:
            tar_id: tar 文件 ID

        Returns:
            tar 文件 URL，如果不存在则返回 None
        """
        tar_id = int(tar_id)

        # 查找文档
        doc = self.collection.find_one({"_id": _id})
        if not doc:
            self.logger.warning(f"未找到 ID 为 {_id} 的 tar 文件记录")
            return None

        # 返回 URL
        url = doc.get("url")
        if not url:
            self.logger.warning(f"ID 为 {_id} 的记录没有 URL 字段")
            return None

        return url