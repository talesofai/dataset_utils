#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
图像转换器，提供统一的图像处理接口
使用 Pillow 库实现
"""

import os
import concurrent.futures
import time
from typing import Tuple, List, Optional, Dict, Any, Set, Union
from PIL import Image
from dataset_utils.utils.logger import setup_logger
from dataset_utils.config import LOG_LEVEL_INT
from ._image_processor import (
    read_image, save_image, convert_color, resize_image,
    find_closest_bucket, ResizeMode, ColorMode
)

# 配置日志
logger = setup_logger(__name__, LOG_LEVEL_INT)

def convert(
    image_path: str,
    output_path: Optional[str] = None,
    resize: Optional[Tuple[int, int]] = None,
    resize_mode: ResizeMode = ResizeMode.PROPORTIONAL,
    color_mode: Optional[ColorMode] = None,
    buckets: Optional[List[Tuple[int, int]]] = None,
    padding_color: Tuple[int, int, int] = (255, 255, 255),
    format: Optional[str] = None,
    quality: int = 85,
    resampling: int = Image.BICUBIC,
    optimize: bool = True,
    keep_exif: bool = True,
    progressive: bool = True,
    dpi: Optional[Tuple[int, int]] = None
) -> Dict[str, Any]:
    """
    转换单个图像

    Args:
        image_path: 图像文件路径
        output_path: 输出文件路径，如果为None则使用原路径+后缀
        resize: 调整大小的目标尺寸 (宽度, 高度)
        resize_mode: 调整大小的模式
        color_mode: 目标颜色模式
        buckets: 尺寸桶列表，用于选择最接近的尺寸
        padding_color: 填充颜色 (R, G, B)
        format: 输出格式，如'WEBP', 'JPEG', 'PNG'等，如果为None则保持原格式
        quality: 图像质量(1-100)，用于JPEG和WEBP格式
        resampling: 重采样方法，如 Image.BICUBIC, Image.BICUBIC等
        optimize: 是否优化输出文件大小
        keep_exif: 是否保留EXIF元数据
        progressive: 是否使用渐进式保存（仅JPEG有效）
        dpi: 图像分辨率设置，如(300, 300)

    Returns:
        转换结果信息
    """
    logger.info(f"开始处理图像: {image_path}")

    try:
        # 读取图像
        image = read_image(image_path)

        # 获取原始尺寸
        width, height = image.size
        original_size = (width, height)
        logger.info(f"原始尺寸: {width}x{height}, 模式: {image.mode}")

        # 处理尺寸桶
        target_size = resize
        if buckets and (resize is None or resize_mode != ResizeMode.PROPORTIONAL):
            bucket_size = find_closest_bucket(width, height, buckets)
            logger.info(f"选择的尺寸桶: {bucket_size}")

            if resize is None:
                target_size = bucket_size
            else:
                # 如果同时指定了resize和buckets，先应用buckets再应用resize
                image = resize_image(image, bucket_size, resize_mode, padding_color, resampling)
                width, height = image.size

        # 调整大小
        if target_size and (width != target_size[0] or height != target_size[1]):
            logger.info(f"调整图像大小: {width}x{height} -> {target_size[0]}x{target_size[1]}, 模式: {resize_mode}")
            image = resize_image(image, target_size, resize_mode, padding_color, resampling)

        # 转换颜色模式
        if color_mode:
            logger.info(f"转换颜色模式: {image.mode} -> {color_mode.value}")
            image = convert_color(image, color_mode)

        # 确定输出路径和格式
        file_name, file_ext = os.path.splitext(image_path)
        output_format = format

        if output_path is None:
            if format:
                format_ext = format.lower() if format.lower() != 'jpeg' else 'jpg'
                output_path = f"{file_name}_converted.{format_ext}"
            else:
                output_path = f"{file_name}_converted{file_ext}"

        # 如果指定了输出路径但没有指定格式，尝试从输出路径推断格式
        if output_format is None and output_path:
            _, ext = os.path.splitext(output_path)
            if ext:
                output_format = ext[1:].upper()
                if output_format == 'JPG':
                    output_format = 'JPEG'

        # 确保模式兼容保存格式
        if output_format in ['JPEG', 'JPG'] and image.mode not in ['RGB', 'L']:
            image = image.convert('RGB')
            logger.info(f"为JPEG格式转换模式: {image.mode} -> RGB")

        if output_format == 'WEBP' and image.mode not in ['RGB', 'RGBA']:
            image = image.convert('RGB')
            logger.info(f"为WEBP格式转换模式: {image.mode} -> RGB")

        # 保存图像
        logger.info(f"保存图像为: {output_path}, 格式: {output_format if output_format else '(自动)'}")

        save_image(
            image,
            output_path,
            format=output_format,
            quality=quality,
            optimize=optimize,
            keep_exif=keep_exif,
            progressive=progressive,
            dpi=dpi
        )

        # 获取处理后的尺寸和最终格式
        final_width, final_height = image.size
        final_format = output_format if output_format else os.path.splitext(output_path)[1][1:].upper()
        if final_format == 'JPG':
            final_format = 'JPEG'

        logger.info(f"图像处理完成，已保存到: {output_path}")

        # 返回处理结果
        return {
            "success": True,
            "input_path": image_path,
            "output_path": output_path,
            "original_size": original_size,
            "final_size": (final_width, final_height),
            "mode": image.mode,
            "format": final_format
        }

    except Exception as e:
        logger.error(f"处理图像失败: {str(e)}")
        return {
            "success": False,
            "input_path": image_path,
            "error": str(e)
        }

def resize_by_short_edge(
    image: Image.Image,
    size: int,
    only_shrink: bool = True,
    resampling: int = Image.BICUBIC
) -> Image.Image:
    """
    根据短边尺寸调整图像大小，保持宽高比

    Args:
        image: 输入图像
        size: 短边目标尺寸
        only_shrink: 如果为True，只缩小不放大
        resampling: 重采样方法

    Returns:
        调整大小后的图像
    """
    width, height = image.size
    short_edge = min(width, height)

    # 如果只缩小且短边已经小于目标尺寸，则不调整
    if only_shrink and short_edge <= size:
        return image

    # 计算新尺寸，保持宽高比
    if width <= height:
        new_width = size
        new_height = int(height * size / width)
    else:
        new_height = size
        new_width = int(width * size / height)

    return resize_image(
        image,
        (new_width, new_height),
        ResizeMode.PROPORTIONAL,
        resampling=resampling
    )

def convert_to_webp(
    image_path: str,
    output_path: str,
    size: Optional[int] = None,
    quality: int = 85,
    only_shrink: bool = True,
    resampling: int = Image.BICUBIC,
    optimize: bool = True,
    keep_exif: bool = True,
    method: int = 6  # WebP编码质量/速度权衡，0(最快)到6(最佳质量)
) -> Optional[str]:
    """
    将单个图像转换为WebP格式

    Args:
        image_path: 源图像路径
        output_path: 输出WebP文件路径
        size: 短边目标尺寸，如果为None则保持原始尺寸
        quality: WebP质量 (1-100)
        only_shrink: 如果为True，只缩小不放大
        resampling: 重采样方法
        optimize: 是否优化输出文件大小
        keep_exif: 是否保留EXIF元数据
        method: WebP编码方法，数值越大压缩质量越好但越慢

    Returns:
        输出文件路径，如果失败则返回None
    """
    try:
        # 如果输出文件已存在且更新时间晚于输入文件，跳过
        if os.path.exists(output_path) and os.path.getmtime(output_path) > os.path.getmtime(image_path):
            logger.debug(f"跳过已存在的文件: {output_path}")
            return output_path

        # 读取图像
        image = read_image(image_path)

        # 调整大小（如果需要）
        if size is not None:
            width, height = image.size
            logger.debug(f"原始尺寸: {width}x{height}")

            image = resize_by_short_edge(image, size, only_shrink, resampling)

            new_width, new_height = image.size
            if (new_width, new_height) != (width, height):
                logger.debug(f"调整图像大小: {width}x{height} -> {new_width}x{new_height}")

        # 保存为WebP
        save_params = {
            'format': 'WEBP',
            'quality': quality,
            'optimize': optimize,
            'keep_exif': keep_exif,
            'method': method  # WebP特有参数，需要单独处理
        }

        # 方法参数需要单独传递
        webp_params = {'method': method}

        # 确保图像模式兼容WebP
        if image.mode not in ('RGB', 'RGBA'):
            image = image.convert('RGB')
            logger.debug(f"转换图像模式: {image.mode} -> RGB")

        # 确保输出目录存在
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        # 保存图像，WebP特有参数直接传递
        image.save(
            output_path,
            'WEBP',
            quality=quality,
            optimize=optimize,
            **webp_params
        )

        logger.debug(f"保存WebP图像: {output_path}, 质量: {quality}, 方法: {method}")

        # 保留原始文件的修改时间和访问时间
        src_stat = os.stat(image_path)
        os.utime(output_path, (src_stat.st_atime, src_stat.st_mtime))

        return output_path

    except Exception as e:
        logger.error(f"处理图片 {image_path} 时出错: {str(e)}")
        return None

def batch_convert(
    image_paths: List[str],
    output_dir: Optional[str] = None,
    workers: int = os.cpu_count(),
    progress_update_interval: float = 2.0,
    **kwargs
) -> List[Dict[str, Any]]:
    """
    批量转换图像

    Args:
        image_paths: 图像文件路径列表
        output_dir: 输出目录
        workers: 并行工作线程数，默认使用所有CPU核心
        progress_update_interval: 进度更新间隔（秒）
        **kwargs: 传递给convert函数的其他参数

    Returns:
        转换结果列表
    """
    if not image_paths:
        logger.warning("没有提供图像路径列表")
        return []

    total_images = len(image_paths)
    logger.info(f"开始批量转换 {total_images} 个图像文件")

    if 'format' in kwargs:
        format_name = kwargs['format']
        logger.info(f"输出格式: {format_name}")

    # 设置格式后缀映射
    format_ext_map = {
        'JPEG': '.jpg',
        'PNG': '.png',
        'WEBP': '.webp',
        'GIF': '.gif',
        'BMP': '.bmp',
        'TIFF': '.tiff'
    }

    # 结果列表
    results = []
    processed_count = 0
    success_count = 0
    start_time = time.time()
    last_update_time = start_time

    # 定义处理单个图片的函数
    def process_image(image_path: str) -> Dict[str, Any]:
        # 确定输出路径
        if output_dir:
            file_name = os.path.basename(image_path)
            base_name, ext = os.path.splitext(file_name)

            # 如果指定了输出格式，使用对应的扩展名
            if 'format' in kwargs:
                format_name = kwargs['format']
                format_ext = format_ext_map.get(format_name, f".{format_name.lower()}")
                output_path = os.path.join(output_dir, f"{base_name}{format_ext}")
            else:
                output_path = os.path.join(output_dir, f"{base_name}_converted{ext}")
        else:
            output_path = None

        # 转换图像
        return convert(image_path, output_path=output_path, **kwargs)

    # 确保输出目录存在
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # 使用线程池并行处理
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        # 提交所有任务
        future_to_path = {executor.submit(process_image, path): path for path in image_paths}

        # 处理结果
        for future in concurrent.futures.as_completed(future_to_path):
            image_path = future_to_path[future]
            try:
                result = future.result()
                results.append(result)

                # 更新成功计数
                if result.get("success", False):
                    success_count += 1

                # 更新进度信息
                processed_count += 1
                current_time = time.time()

                # 定期更新进度
                if (current_time - last_update_time >= progress_update_interval or
                    processed_count == 1 or processed_count == total_images):

                    # 计算完成百分比
                    percent = processed_count / total_images * 100

                    # 计算已运行时间和预估剩余时间
                    elapsed_time = current_time - start_time
                    if processed_count > 0:
                        avg_time_per_image = elapsed_time / processed_count
                        remaining_images = total_images - processed_count
                        eta = avg_time_per_image * remaining_images
                        eta_str = f", 预计剩余时间: {eta:.1f}秒" if eta < 60 else \
                                f", 预计剩余时间: {eta/60:.1f}分钟" if eta < 3600 else \
                                f", 预计剩余时间: {eta/3600:.1f}小时"
                    else:
                        eta_str = ""

                    # 计算处理速度
                    speed = processed_count / elapsed_time if elapsed_time > 0 else 0

                    # 显示进度条
                    bar_length = 30
                    filled_length = int(bar_length * processed_count / total_images)
                    bar = '█' * filled_length + '░' * (bar_length - filled_length)

                    logger.info(
                        f"进度: [{bar}] {processed_count}/{total_images} ({percent:.1f}%) "
                        f"- 速度: {speed:.1f}张/秒{eta_str}"
                    )

                    last_update_time = current_time

            except Exception as e:
                error_msg = f"处理图像 {image_path} 失败: {str(e)}"
                logger.error(error_msg)
                results.append({
                    "success": False,
                    "input_path": image_path,
                    "error": error_msg
                })

    # 计算总耗时
    total_time = time.time() - start_time
    hours, remainder = divmod(total_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    time_str = f"{int(hours)}小时{int(minutes)}分钟{seconds:.1f}秒" if hours > 0 else \
              f"{int(minutes)}分钟{seconds:.1f}秒" if minutes > 0 else \
              f"{seconds:.1f}秒"

    # 统计结果
    if total_time > 0:
        avg_time = total_time / total_images
        logger.info(f"平均处理速度: {1/avg_time:.2f}张/秒 ({avg_time*1000:.1f}毫秒/张)")

    logger.info(f"批量处理完成: 总数={total_images}, 成功={success_count}, 失败={total_images-success_count}, 总耗时: {time_str}")

    return results

def batch_convert_to_webp(
    source_dir: str,
    output_base_dir: Optional[str] = None,
    sizes: List[int] = [256, 1024, 2048],
    quality: int = 85,
    workers: int = os.cpu_count(),
    progress_update_interval: float = 2.0,
    supported_formats: Set[str] = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'},
    only_shrink: bool = True,
    resampling: int = Image.BICUBIC,
    optimize: bool = True,
    keep_exif: bool = True,
    method: int = 4,
    keep_folder_structure: bool = True
) -> Dict[str, Dict[int, Optional[str]]]:
    """
    批量将图像转换为WebP格式

    Args:
        source_dir: 源图像目录
        output_base_dir: 输出基础目录，如果为None则使用source_dir/webp
        sizes: 短边尺寸列表
        quality: WebP质量 (1-100)
        workers: 并行工作线程数
        progress_update_interval: 进度更新间隔（秒）
        supported_formats: 支持的输入图片格式
        only_shrink: 如果为True，只缩小不放大
        resampling: 重采样方法
        optimize: 是否优化输出文件大小
        keep_exif: 是否保留EXIF元数据
        method: WebP编码方法，0(最快)到6(最佳质量)
        keep_folder_structure: 是否保持源目录的文件夹结构

    Returns:
        嵌套字典 {图片路径: {尺寸: 输出路径}}
    """
    # 验证并设置目录
    source_dir = os.path.abspath(source_dir)
    if not os.path.exists(source_dir):
        raise ValueError(f"源目录不存在: {source_dir}")

    # 设置输出基础目录
    if output_base_dir is None:
        output_base_dir = os.path.join(source_dir, "webp")
    else:
        output_base_dir = os.path.abspath(output_base_dir)

    # 确保质量在1-100范围内
    quality = max(1, min(100, quality))

    # 确保method在有效范围内
    method = max(0, min(6, method))

    # 创建输出目录
    output_dirs = {}
    for size in sizes:
        size_dir = os.path.join(output_base_dir, f"{size}x")
        os.makedirs(size_dir, exist_ok=True)
        output_dirs[size] = size_dir
        logger.info(f"创建输出目录: {size_dir}")

    # 扫描源目录中的所有支持格式的图片
    logger.info(f"开始扫描目录: {source_dir}")
    image_files = []
    for root, _, files in os.walk(source_dir):
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext in supported_formats:
                image_files.append(file_path)

    total_images = len(image_files)
    logger.info(f"扫描完成，找到 {total_images} 个图片文件")

    if total_images == 0:
        logger.warning(f"未找到任何支持的图片文件")
        return {}

    # 计算总任务数（每个图片 * 尺寸数）
    total_tasks = total_images * len(sizes)
    logger.info(f"开始转换 {total_images} 个图片文件 -> {len(sizes)} 种尺寸")
    logger.info(f"总任务数: {total_tasks} (图片数 * 尺寸数)")
    logger.info(f"WebP质量: {quality}, 优化: {optimize}, 保留EXIF: {keep_exif}, 编码方法: {method}")

    # 结果字典
    results = {}
    processed_count = 0
    start_time = time.time()
    last_update_time = start_time

    # 定义处理单个图片的函数
    def process_image(image_path: str) -> Dict[int, Optional[str]]:
        result = {}
        rel_path = os.path.relpath(image_path, source_dir)

        for size in sizes:
            # 构建输出路径
            if keep_folder_structure:
                dir_name, file_name = os.path.split(rel_path)
                file_name_without_ext, _ = os.path.splitext(file_name)
                webp_name = file_name_without_ext + ".webp"

                if dir_name:
                    output_dir = os.path.join(output_dirs[size], dir_name)
                    os.makedirs(output_dir, exist_ok=True)
                    output_path = os.path.join(output_dir, webp_name)
                else:
                    output_path = os.path.join(output_dirs[size], webp_name)
            else:
                # 不保持目录结构，全部图片放在同一目录
                file_name = os.path.basename(image_path)
                file_name_without_ext, _ = os.path.splitext(file_name)
                # 添加哈希值避免同名文件冲突
                import hashlib
                path_hash = hashlib.md5(image_path.encode()).hexdigest()[:8]
                webp_name = f"{file_name_without_ext}_{path_hash}.webp"
                output_path = os.path.join(output_dirs[size], webp_name)

            # 转换图片
            result[size] = convert_to_webp(
                image_path,
                output_path,
                size,
                quality,
                only_shrink,
                resampling,
                optimize,
                keep_exif,
                method
            )

        return result

    # 使用线程池并行处理
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        # 提交所有任务
        future_to_path = {executor.submit(process_image, path): path for path in image_files}

        # 处理结果
        for future in concurrent.futures.as_completed(future_to_path):
            image_path = future_to_path[future]
            try:
                result = future.result()
                results[image_path] = result

                # 更新进度信息
                processed_count += 1
                current_time = time.time()

                # 定期更新进度
                if (current_time - last_update_time >= progress_update_interval or
                    processed_count == 1 or processed_count == total_images):

                    # 计算完成百分比
                    percent = processed_count / total_images * 100

                    # 计算已运行时间和预估剩余时间
                    elapsed_time = current_time - start_time
                    if processed_count > 0:
                        avg_time_per_image = elapsed_time / processed_count
                        remaining_images = total_images - processed_count
                        eta = avg_time_per_image * remaining_images
                        eta_str = f", 预计剩余时间: {eta:.1f}秒" if eta < 60 else \
                                f", 预计剩余时间: {eta/60:.1f}分钟" if eta < 3600 else \
                                f", 预计剩余时间: {eta/3600:.1f}小时"
                    else:
                        eta_str = ""

                    # 计算处理速度
                    speed = processed_count / elapsed_time if elapsed_time > 0 else 0

                    # 显示进度条
                    bar_length = 30
                    filled_length = int(bar_length * processed_count / total_images)
                    bar = '█' * filled_length + '░' * (bar_length - filled_length)

                    logger.info(
                        f"进度: [{bar}] {processed_count}/{total_images} ({percent:.1f}%) "
                        f"- 速度: {speed:.1f}张/秒{eta_str}"
                    )

                    last_update_time = current_time

            except Exception as e:
                logger.error(f"处理 {image_path} 时发生异常: {str(e)}")
                results[image_path] = {size: None for size in sizes}

    # 计算总耗时
    total_time = time.time() - start_time
    hours, remainder = divmod(total_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    time_str = f"{int(hours)}小时{int(minutes)}分钟{seconds:.1f}秒" if hours > 0 else \
              f"{int(minutes)}分钟{seconds:.1f}秒" if minutes > 0 else \
              f"{seconds:.1f}秒"

    # 统计结果
    success_count = 0
    failed_sizes = {size: 0 for size in sizes}
    total_output_size = 0
    total_input_size = 0

    for image_path, size_results in results.items():
        if all(size_results.values()):
            success_count += 1
            # 计算原始文件大小
            if os.path.exists(image_path):
                input_size = os.path.getsize(image_path)
                total_input_size += input_size
                # 计算所有输出文件大小
                for output_path in size_results.values():
                    if output_path and os.path.exists(output_path):
                        total_output_size += os.path.getsize(output_path)
        else:
            for size, output_path in size_results.items():
                if output_path is None:
                    failed_sizes[size] += 1

    # 计算压缩比
    compression_ratio = "未知"
    if total_input_size > 0 and total_output_size > 0:
        ratio = total_output_size / total_input_size
        compression_ratio = f"{ratio:.2%}"

    logger.info(f"转换完成: 成功 {success_count}/{total_images} ({success_count/total_images*100:.1f}%), 总耗时: {time_str}")
    logger.info(f"压缩比例: {compression_ratio} (输出总大小 / 输入总大小)")

    if total_time > 0:
        avg_time = total_time / total_images
        logger.info(f"平均处理速度: {1/avg_time:.2f}张/秒 ({avg_time*1000:.1f}毫秒/张)")

    for size, count in failed_sizes.items():
        if count > 0:
            logger.warning(f"尺寸 {size}x 失败数量: {count}")

    return results
