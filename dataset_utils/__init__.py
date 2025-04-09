"""
dataset_utils - 一个综合性的数据集处理工具包

该包提供各种数据集处理功能，包括图像处理、压缩文件处理等。
"""

__version__ = "0.1.0"
__author__ = "shiertier"

from dataset_utils.image_utils import (
    convert, batch_convert,
    convert_to_webp, batch_convert_to_webp,
    resize_by_short_edge
)

# 导出MongoDB客户端
from dataset_utils.mongo_clients import MongoDBClient, PixivDB