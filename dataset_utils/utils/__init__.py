"""
通用工具模块

提供日志记录、文件下载等通用功能
"""

from .logger import setup_logger, get_logger
from .file_downloader import download_file, download_files