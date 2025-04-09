"""
图像转换器示例
使用 Pillow 实现
"""

import os
from image_utils._convert_image import convert, batch_convert, ResizeMode, ColorMode

def single_image_example():
    """单图像转换示例"""
    # 示例1: 简单调整大小
    result = convert(
        "samples/image1.jpg",
        output_path="output/image1_resized.jpg",
        resize=(800, 600),
        resize_mode=ResizeMode.PROPORTIONAL
    )
    print(f"简单调整大小: {'成功' if result['success'] else '失败'}")

    # 示例2: 调整大小并裁剪
    result = convert(
        "samples/image2.jpg",
        output_path="output/image2_cropped.jpg",
        resize=(400, 400),
        resize_mode=ResizeMode.CROP
    )
    print(f"调整大小并裁剪: {'成功' if result['success'] else '失败'}")

    # 示例3: 调整大小并填充
    result = convert(
        "samples/image3.jpg",
        output_path="output/image3_padded.jpg",
        resize=(600, 400),
        resize_mode=ResizeMode.PADDING,
        padding_color=(0, 0, 0)  # 黑色填充
    )
    print(f"调整大小并填充: {'成功' if result['success'] else '失败'}")

    # 示例4: 转换为灰度图
    result = convert(
        "samples/image4.jpg",
        output_path="output/image4_gray.jpg",
        color_mode=ColorMode.GRAY
    )
    print(f"转换为灰度图: {'成功' if result['success'] else '失败'}")

    # 示例5: 使用尺寸桶
    buckets = [(320, 240), (640, 480), (800, 600), (1024, 768)]
    result = convert(
        "samples/image5.jpg",
        output_path="output/image5_bucketed.jpg",
        buckets=buckets
    )
    print(f"使用尺寸桶: {'成功' if result['success'] else '失败'}")

    # 示例6: 组合多种操作
    result = convert(
        "samples/image6.jpg",
        output_path="output/image6_combined.jpg",
        resize=(800, 600),
        resize_mode=ResizeMode.PADDING,
        color_mode=ColorMode.RGB,
        padding_color=(255, 0, 0)  # 红色填充
    )
    print(f"组合多种操作: {'成功' if result['success'] else '失败'}")

def batch_example():
    """批量转换示例"""
    # 获取所有样本图像
    sample_dir = "samples"
    image_paths = [
        os.path.join(sample_dir, f)
        for f in os.listdir(sample_dir)
        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))
    ]

    # 批量转换
    results = batch_convert(
        image_paths,
        output_dir="output/batch",
        resize=(640, 480),
        resize_mode=ResizeMode.PROPORTIONAL,
        color_mode=ColorMode.RGB
    )

    # 打印结果
    success_count = sum(1 for r in results if r.get("success", False))
    print(f"批量处理结果: 总数={len(results)}, 成功={success_count}, 失败={len(results)-success_count}")

if __name__ == "__main__":
    # 确保输出目录存在
    os.makedirs("output", exist_ok=True)
    os.makedirs("output/batch", exist_ok=True)

    print("=== 单图像转换示例 ===")
    single_image_example()

    print("\n=== 批量转换示例 ===")
    batch_example()