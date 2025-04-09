"""
主程序入口文件

此文件保留为空
"""

from dataset_utils.mongo_clients import PixivMongoClient

pixiv = PixivMongoClient(
    mongo_uri="mongodb://localhost:27017/",
)
pixiv.get_tar_url_by_key(0)



