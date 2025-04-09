import os
import tarfile
import tempfile
import shutil
from typing import Optional
from dataset_utils.utils.logger import setup_logger
from dataset_utils.config import LOG_LEVEL_INT

# 配置日志
logger = setup_logger(__name__, LOG_LEVEL_INT)

def extract(
    tar_path: str,
    target_dir: Optional[str] = None,
    extract_base_dir: str = "./extracted_files"
) -> Optional[str]:
    """
    解压 tar 文件的纯函数实现

    Args:
        tar_path: tar 文件路径
        target_dir: 解压目标目录，如果为 None 则使用默认目录
        extract_base_dir: 默认解压基础目录，当 target_dir 为 None 时使用

    Returns:
        解压目录路径，如果解压失败则返回 None
    """
    if not os.path.exists(tar_path):
        logger.error(f"tar 文件不存在: {tar_path}")
        return None

    # 获取文件名（不含扩展名）作为解压目录
    file_name = os.path.basename(tar_path)
    file_name_without_ext = os.path.splitext(file_name)[0]

    # 确定解压目标目录
    if target_dir is None:
        # 确保基础目录存在
        os.makedirs(extract_base_dir, exist_ok=True)
        target_dir = os.path.join(extract_base_dir, file_name_without_ext)

    # 如果目标目录已存在并且有内容，可能已经解压过
    if os.path.exists(target_dir) and os.listdir(target_dir):
        logger.info(f"目标目录已存在且非空，可能已解压: {target_dir}")
        return target_dir

    # 创建目标目录
    os.makedirs(target_dir, exist_ok=True)

    logger.info(f"开始解压: {tar_path} -> {target_dir}")

    # 使用临时目录进行解压
    with tempfile.TemporaryDirectory() as temp_dir:
        # 解压到临时目录
        with tarfile.open(tar_path) as tar:
            tar.extractall(path=temp_dir)

        # 将文件从临时目录移动到目标目录
        for item in os.listdir(temp_dir):
            item_path = os.path.join(temp_dir, item)
            target_path = os.path.join(target_dir, item)

            # 如果是目录，移动整个目录
            if os.path.isdir(item_path):
                shutil.move(item_path, target_path)
            else:
                shutil.copy2(item_path, target_path)

    logger.info(f"解压完成: {target_dir}")
    return target_dir