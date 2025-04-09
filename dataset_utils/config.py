#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置模块，用于管理全局日志配置项
"""

import os
import logging

# 日志配置
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}
LOG_LEVEL_INT = LOG_LEVEL_MAP.get(LOG_LEVEL.upper(), logging.INFO)