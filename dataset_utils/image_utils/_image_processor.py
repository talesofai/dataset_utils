"""
基础图像处理模块，提供图像变换的核心功能
使用 Pillow 库实现
"""

import os
from enum import Enum
from typing import Tuple, List, Optional, Union
from PIL import Image, ImageOps

class ResizeMode(str, Enum):
    """调整大小的模式"""
    PROPORTIONAL = "proportional"  # 等比例缩放
    CROP = "crop"                  # 缩放后中心裁剪
    PADDING = "padding"            # 缩放后填充

class ColorMode(str, Enum):
    """颜色模式"""
    RGB = "rgb"
    RGBA = "rgba"
    GRAY = "L"  # Pillow 使用 "L" 表示灰度图

def read_image(image_path: str) -> Image.Image:
    """
    读取图像文件

    Args:
        image_path: 图像文件路径

    Returns:
        PIL图像对象
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图像文件不存在: {image_path}")

    try:
        image = Image.open(image_path)
        # 立即加载图像数据，避免文件句柄问题
        image.load()
        return image
    except Exception as e:
        raise ValueError(f"无法读取图像: {image_path}, 错误: {str(e)}")

def save_image(
    image: Image.Image,
    output_path: str,
    format: Optional[str] = None,
    quality: int = 90,
    optimize: bool = True,
    keep_exif: bool = True,
    progressive: bool = True,
    subsampling: int = -1,
    dpi: Optional[Tuple[int, int]] = None
) -> str:
    """
    保存图像到文件，支持更多输出选项

    Args:
        image: PIL图像对象
        output_path: 输出文件路径
        format: 输出格式，如'JPEG', 'PNG', 'WEBP'等，如果为None则从文件扩展名推断
        quality: 图像质量(1-100)，用于JPEG和WEBP格式
        optimize: 是否尝试优化图像文件大小
        keep_exif: 是否保留EXIF元数据
        progressive: 是否使用渐进式保存（仅JPEG格式有效）
        subsampling: 色度二次采样，仅适用于JPEG
                     0: 4:4:4, 1: 4:2:2, 2: 4:2:0, -1: 默认
        dpi: 图像分辨率(dots per inch)，如(300, 300)

    Returns:
        保存的文件路径
    """
    # 确保输出目录存在
    output_dir = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(output_dir, exist_ok=True)

    # 从文件扩展名推断格式（如果未指定）
    if format is None:
        _, ext = os.path.splitext(output_path)
        if ext:
            format = ext[1:].upper()
            # 特殊处理JPG -> JPEG
            if format == 'JPG':
                format = 'JPEG'

    # 验证并调整参数
    if quality is not None:
        quality = max(1, min(100, quality))  # 确保质量在1-100范围内

    try:
        # 准备保存参数
        save_args = {}

        # 如果需要保留EXIF数据
        if keep_exif and hasattr(image, 'info') and 'exif' in image.info:
            save_args['exif'] = image.info['exif']

        # 根据不同格式设置特定参数
        if format in ['JPEG', 'WEBP']:
            save_args['quality'] = quality
            save_args['optimize'] = optimize

            if format == 'JPEG':
                save_args['progressive'] = progressive
                if subsampling != -1:
                    save_args['subsampling'] = subsampling

        elif format == 'PNG':
            save_args['optimize'] = optimize

        # 添加DPI信息（如果提供）
        if dpi is not None:
            save_args['dpi'] = dpi

        # 保存图像
        if format:
            # 确保图像模式兼容当前格式
            if format == 'JPEG' and image.mode not in ['RGB', 'L']:
                image = image.convert('RGB')

            image.save(output_path, format, **save_args)
        else:
            # 如果无法确定格式，使用默认保存
            image.save(output_path)

        return output_path

    except ValueError as e:
        # 格式错误等值错误
        error_msg = f"保存图像值错误: {output_path}, 格式: {format}, 错误: {str(e)}"
        raise ValueError(error_msg)
    except OSError as e:
        # 文件IO错误
        error_msg = f"保存图像IO错误: {output_path}, 格式: {format}, 错误: {str(e)}"
        raise IOError(error_msg)
    except Exception as e:
        # 其他未预期的错误
        error_msg = f"保存图像失败: {output_path}, 格式: {format}, 错误: {type(e).__name__}: {str(e)}"
        raise IOError(error_msg)

def convert_color(image: Image.Image, target_mode: ColorMode) -> Image.Image:
    """
    转换图像颜色模式

    Args:
        image: 输入图像
        target_mode: 目标颜色模式

    Returns:
        转换后的图像
    """
    # 如果已经是目标模式，直接返回
    if image.mode == target_mode.value:
        return image

    # 转换颜色模式
    try:
        return image.convert(target_mode.value)
    except Exception as e:
        raise ValueError(f"颜色模式转换失败: {image.mode} -> {target_mode.value}, 错误: {str(e)}")

def find_closest_bucket(width: int, height: int, buckets: List[Tuple[int, int]]) -> Tuple[int, int]:
    """
    找到最接近的尺寸桶

    Args:
        width: 图像宽度
        height: 图像高度
        buckets: 尺寸桶列表，每个元素为(宽度, 高度)

    Returns:
        最接近的尺寸桶
    """
    if not buckets:
        raise ValueError("尺寸桶列表不能为空")

    # 计算原始图像的宽高比
    aspect_ratio = width / height

    # 找到最接近的桶
    closest_bucket = None
    min_diff = float('inf')

    for bucket_width, bucket_height in buckets:
        bucket_ratio = bucket_width / bucket_height
        diff = abs(aspect_ratio - bucket_ratio)

        if diff < min_diff:
            min_diff = diff
            closest_bucket = (bucket_width, bucket_height)

    return closest_bucket

def resize_image(
    image: Image.Image,
    target_size: Tuple[int, int],
    mode: ResizeMode = ResizeMode.PROPORTIONAL,
    padding_color: Tuple[int, int, int] = (255, 255, 255),
    resampling: int = Image.LANCZOS
) -> Image.Image:
    """
    调整图像大小

    Args:
        image: 输入图像
        target_size: 目标尺寸 (宽度, 高度)
        mode: 调整模式
        padding_color: 填充颜色 (R, G, B)
        resampling: 重采样方法，如 Image.LANCZOS, Image.BICUBIC, Image.BILINEAR 等

    Returns:
        调整大小后的图像
    """
    target_width, target_height = target_size
    width, height = image.size

    # 根据不同模式处理
    if mode == ResizeMode.PROPORTIONAL:
        # 等比例缩放
        ratio = min(target_width / width, target_height / height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        return image.resize((new_width, new_height), resampling)

    elif mode == ResizeMode.CROP:
        # 等比例缩放后中心裁剪
        ratio = max(target_width / width, target_height / height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        resized = image.resize((new_width, new_height), resampling)

        # 中心裁剪
        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
        right = left + target_width
        bottom = top + target_height
        return resized.crop((left, top, right, bottom))

    elif mode == ResizeMode.PADDING:
        # 等比例缩放后填充
        ratio = min(target_width / width, target_height / height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        resized = image.resize((new_width, new_height), resampling)

        # 创建目标尺寸的空白图像并粘贴调整大小后的图像
        result = Image.new(image.mode, (target_width, target_height), padding_color)
        paste_x = (target_width - new_width) // 2
        paste_y = (target_height - new_height) // 2
        result.paste(resized, (paste_x, paste_y))
        return result

    # 默认情况，直接调整大小
    return image.resize(target_size, resampling)