#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 根据项目需要添加依赖
requirements = [
    "pillow",
    "numpy",
    "tqdm",
    "pymongo",  # 假设mongo_clients目录需要这个依赖
]

setup(
    name="dataset_utils",
    version="0.1.0",
    author="shiertier",
    author_email="junjie.text@gmail.com",
    description="数据集处理工具包，支持图像处理、压缩文件处理等功能",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/dataset_utils",  # 请替换为实际项目URL
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
)