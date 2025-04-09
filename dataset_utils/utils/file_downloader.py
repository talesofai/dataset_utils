#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件下载工具模块，用于从 URL 下载文件
"""

import os
import requests
import time
from typing import Optional, Callable, Dict, Any, List
from dataset_utils.utils.logger import setup_logger
from dataset_utils.config import LOG_LEVEL_INT

# 配置日志
logger = setup_logger(__name__, LOG_LEVEL_INT)

# 默认下载目录
DEFAULT_DOWNLOAD_DIR = "./downloaded_files"
os.makedirs(DEFAULT_DOWNLOAD_DIR, exist_ok=True)

def download_file(
    url: str,
    filename: str = None,
    file_id: str = None,
    extension: str = None,
    download_dir: str = None,
    headers: Dict[str, str] = None,
    progress_callback: Callable[[float, int, int], Any] = None,
    chunk_size: int = 8192,
    resume: bool = True
) -> Optional[str]:
    """
    下载文件

    Args:
        url: 文件 URL
        filename: 自定义文件名（如果提供，将直接使用该文件名）
        file_id: 文件 ID 或标识，用于命名（当 filename 未提供时使用）
        extension: 文件扩展名（默认为 None，将从 URL 或响应头中推断）
        download_dir: 指定下载目录，如果为 None 则使用默认目录
        headers: 请求头字典
        progress_callback: 进度回调函数，接收参数：百分比、已下载大小、总大小
        chunk_size: 每次读取的块大小
        resume: 是否支持断点续传

    Returns:
        下载文件的本地路径，如果下载失败则返回 None
    """
    # 确定下载目录
    target_dir = download_dir if download_dir else DEFAULT_DOWNLOAD_DIR
    os.makedirs(target_dir, exist_ok=True)

    # 确定文件名
    if filename:
        local_filename = filename
    else:
        if not file_id:
            # 从URL中获取基本文件名但先不包含扩展名
            file_id = os.path.splitext(os.path.basename(url).split('?')[0])[0]

        # 确定扩展名
        if not extension:
            # 从 URL 中提取扩展名
            url_ext = os.path.splitext(url.split('?')[0])[1]
            if url_ext:
                extension = url_ext
            else:
                extension = '.tar'  # 默认扩展名

        # 确保扩展名以点开头
        if extension and not extension.startswith('.'):
            extension = f'.{extension}'

        local_filename = f"{file_id}{extension}"

    local_path = os.path.join(target_dir, local_filename)

    # 初始化请求头
    if headers is None:
        headers = {}

    # 文件已存在的处理
    file_size = 0
    if os.path.exists(local_path):
        file_size = os.path.getsize(local_path)
        if file_size > 0:
            if not resume:
                logger.info(f"文件已存在: {local_path}")
                return local_path
            else:
                # 断点续传
                headers['Range'] = f'bytes={file_size}-'
                logger.info(f"断点续传: {local_path}，已下载 {file_size/(1024*1024):.2f}MB")

    logger.info(f"开始下载: {url} 到 {local_path}")

    # 使用流式下载以处理大文件
    try:
        response = requests.get(url, stream=True, timeout=30, headers=headers)

        # 处理断点续传的情况
        if resume and file_size > 0 and response.status_code == 206:
            mode = 'ab'  # 追加模式
        else:
            mode = 'wb'  # 写入模式
            file_size = 0

        if response.status_code not in [200, 206]:
            logger.error(f"下载失败，状态码: {response.status_code}")
            return None

        # 获取文件大小
        if 'content-length' in response.headers:
            content_length = int(response.headers.get('content-length', 0))
            total_size = file_size + content_length
        else:
            total_size = 0

        downloaded = file_size
        last_log_time = time.time()  # 记录上次日志时间

        # 下载文件
        with open(local_path, mode) as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)

                    # 计算进度
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100

                        # 调用进度回调
                        if progress_callback:
                            progress_callback(percent, downloaded, total_size)

                        # 每秒打印一次进度
                        current_time = time.time()
                        if current_time - last_log_time >= 1.0:
                            logger.info(f"下载进度: {percent:.2f}% ({downloaded/(1024*1024):.2f}MB / {total_size/(1024*1024):.2f}MB)")
                            last_log_time = current_time

        logger.info(f"下载完成: {local_path}")
        return local_path

    except Exception as e:
        logger.error(f"下载出错: {str(e)}")
        return None

def download_files(urls: List[str], download_dir: str = None, **kwargs) -> List[Optional[str]]:
    """
    批量下载多个文件

    Args:
        urls: URL列表
        download_dir: 下载目录
        **kwargs: 传递给download_file的其他参数

    Returns:
        下载文件路径列表
    """
    results = []
    for url in urls:
        file_path = download_file(url=url, download_dir=download_dir, **kwargs)
        results.append(file_path)
    return results