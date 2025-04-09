"""
WebP 转换器示例
展示如何使用 image_utils.resize 模块将图像批量转换为 WebP 格式
"""

import os
from image_utils._resize import batch_convert_to_webp, convert_to_webp

def single_image_example():
    """单图像转换示例"""
    # 转换单个图像为WebP
    result = convert_to_webp(
        "samples/image1.jpg",
        "output/image1.webp",
        size=800,  # 短边为800像素
        quality=90
    )

    if result:
        print(f"转换成功: {result}")
    else:
        print("转换失败")

def batch_conversion_example():
    """批量转换示例"""
    # 批量转换目录中的所有图像
    results = batch_convert_to_webp(
        source_dir="samples",
        output_base_dir="output/webp",
        sizes=[256, 512, 1024],  # 生成三种尺寸
        quality=85,
        workers=4  # 使用4个线程
    )

    # 统计结果
    total = len(results)
    success = sum(1 for img_results in results.values() if all(img_results.values()))

    print(f"批量转换结果: 总数={total}, 成功={success}, 失败={total-success}")

if __name__ == "__main__":
    # 确保输出目录存在
    os.makedirs("output", exist_ok=True)
    os.makedirs("output/webp", exist_ok=True)

    print("=== 单图像转换示例 ===")
    single_image_example()

    print("\n=== 批量转换示例 ===")
    batch_conversion_example()