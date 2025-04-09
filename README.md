# Dataset Utils

一个综合性的数据集处理工具包，提供图像处理、压缩文件处理等功能。

## 功能特点

- **图像处理**：支持图像格式转换、大小调整等操作
- **压缩文件处理**：支持ZIP、TAR等压缩文件的解压缩
- **MongoDB客户端**：提供MongoDB数据库操作功能
- **通用工具**：提供日志记录、文件下载等通用功能

## 安装方法

### 从PyPI安装（尚未发布）

```bash
pip install dataset-utils
```

### 从源码安装

```bash
git clone https://github.com/talesofai/dataset_utils.git
cd dataset_utils
pip install -e .
```

## 使用方法

### 作为Python库使用

```python
# 导入图像处理模块
from dataset_utils.image_utils import convert_to_webp, batch_convert

# 转换单个文件
convert_to_webp("input.jpg", "output.webp", quality=90)

# 批量转换
batch_convert("input_dir/", "output_dir/", target_format="webp", quality=85, resize=1024)

# 导入其他功能
from dataset_utils.utils import download_file
download_file("https://example.com/file.txt", "local_file.txt")
```

## 开发者文档

### 项目结构

```
dataset_utils/
├── archive_utils/       # 压缩文件处理模块
│   ├── tar/             # TAR文件处理
│   └── zip/             # ZIP文件处理
├── image_utils/         # 图像处理模块
├── mongo_clients/       # MongoDB客户端
└── utils/               # 通用工具
```

## 许可证

MIT