# Image Utils 图像处理工具包

一个功能强大的图像处理工具包，支持批量转换、调整大小、格式转换等多种功能，特别优化了WebP格式的转换。

## 主要功能

- 图像格式转换（支持JPEG、PNG、WebP、GIF、BMP、TIFF等格式）
- 批量处理大量图像（多线程并行处理）
- 智能调整图像大小（等比例缩放、裁剪、填充）
- WebP格式的高效转换和优化
- 保留EXIF元数据
- 丰富的图像质量控制选项
- 实时进度显示和统计信息

## 安装要求

- Python 3.6+
- Pillow 库
- 其他依赖（在requirements.txt中列出）

## 使用方法

### 作为Python库使用

您可以直接在Python脚本中导入和使用：

```python
from image_utils import convert, batch_convert, convert_to_webp, batch_convert_to_webp, resize_by_short_edge

# 转换单个图像
result = convert(
    "input.jpg",
    output_path="output.webp",
    format="WEBP",
    quality=90
)

# 调整图像大小（根据短边）
from PIL import Image
image = Image.open("input.jpg")
resized_image = resize_by_short_edge(image, size=800)
resized_image.save("resized.jpg")

# 批量转换目录中的图像
results = batch_convert_to_webp(
    "input_dir",
    output_base_dir="output_dir",
    sizes=[256, 1024, 2048],
    quality=85,
    workers=4
)
```

## 核心功能详解

### 格式转换

支持多种图像格式之间的转换，包括JPEG、PNG、WebP、GIF、BMP、TIFF等。WebP格式特别优化，提供了额外的控制参数。

### 调整大小模式

- **等比例缩放 (PROPORTIONAL)**: 保持图像宽高比，调整到目标尺寸
- **裁剪 (CROP)**: 等比例缩放后中心裁剪，确保输出图像精确匹配目标尺寸
- **填充 (PADDING)**: 等比例缩放后填充，确保图像完整且匹配目标尺寸

### 重采样方法

- **Lanczos**: 高质量重采样，适合大多数图像（默认）
- **Bicubic**: 双三次插值，质量较好
- **Bilinear**: 双线性插值，速度较快
- **Nearest**: 最近邻插值，速度最快但质量最低

### 批量处理

所有批量处理功能都支持多线程并行处理，充分利用多核CPU提高处理速度。处理过程中会显示实时进度、预计剩余时间和处理速度。

## 使用示例

### 转换单个图像到WebP格式

```python
from image_utils import convert

result = convert(
    "input.jpg",
    output_path="output.webp",
    format="WEBP",
    quality=90,
    optimize=True
)

if result["success"]:
    print(f"转换成功: {result['output_path']}")
    print(f"原始尺寸: {result['original_size']}")
    print(f"最终尺寸: {result['final_size']}")
```

### 批量将目录中的图像转换为WebP格式，生成多种尺寸

```python
from image_utils import batch_convert_to_webp

results = batch_convert_to_webp(
    "input_directory",
    output_base_dir="output_directory",
    sizes=[256, 1024, 2048],
    quality=85,
    workers=8,  # 使用8个线程并行处理
    optimize=True,
    keep_exif=True,
    method=4,  # WebP编码方法 (0-6)
    keep_folder_structure=True
)
```

### 转换多个图像，调整大小并裁剪

```python
from image_utils import batch_convert, ResizeMode
from PIL import Image
import os

image_files = [
    "image1.jpg",
    "image2.png",
    "image3.jpeg"
]

results = batch_convert(
    image_files,
    output_dir="output_directory",
    resize=(800, 600),  # 目标尺寸 (宽度, 高度)
    resize_mode=ResizeMode.CROP,  # 裁剪模式
    format="JPEG",
    quality=85,
    workers=4
)
```

## 开发者API

### 主要函数

- `convert(image_path, output_path=None, ...)`: 转换单个图像
- `batch_convert(image_paths, output_dir=None, workers=os.cpu_count(), ...)`: 批量转换图像
- `convert_to_webp(image_path, output_path, size=None, ...)`: 将单个图像转换为WebP格式
- `batch_convert_to_webp(source_dir, output_base_dir=None, sizes=[256, 1024, 2048], workers=os.cpu_count(), ...)`: 批量将图像转换为WebP格式
- `resize_by_short_edge(image, size, only_shrink=True, ...)`: 根据短边尺寸调整图像大小
- `resize_image(image, target_size, mode=ResizeMode.PROPORTIONAL, ...)`: 基本的图像调整大小功能
- `read_image(image_path)`, `save_image(image, output_path, ...)`: 基本的图像读写功能

### 关键参数

- **format**: 输出格式，如'WEBP', 'JPEG', 'PNG'等
- **quality**: 图像质量(1-100)，用于JPEG和WebP格式
- **resize_mode**: 调整大小的模式(PROPORTIONAL, CROP, PADDING)
- **resampling**: 重采样方法(Image.LANCZOS, Image.BICUBIC等)
- **optimize**: 是否优化输出文件大小
- **keep_exif**: 是否保留EXIF元数据
- **progressive**: 是否使用渐进式保存（仅JPEG有效）
- **workers**: 并行工作线程数，默认使用所有CPU核心

## 性能考虑

- 默认使用所有可用CPU核心进行并行处理
- 对于大量图像的处理，内存使用会随并行线程数增加
- WebP编码方法参数可以根据需要平衡速度和质量
- 处理大分辨率图像时，建议适当降低并行线程数

## 注意事项

- 工具会自动跳过已存在且更新时间较新的输出文件
- 为避免文件名冲突，在不保持目录结构时会添加文件路径的哈希值
- 批量处理结束后会提供统计信息，包括处理速度和压缩比
- 所有批量处理函数都支持多线程，充分利用多核CPU