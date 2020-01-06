#! /usr/bin/python3
# -- coding:UTF-8 --


import os
import time
import logging
from logging.handlers import RotatingFileHandler


def log(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # 设置日志级别

    # 日志文件名
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    path = os.path.join(os.path.join(BASE_DIR, 'logfile'), time.strftime("%Y-%m-%d", time.gmtime()))

    fh = RotatingFileHandler(path, maxBytes=1024 * 1024 * 100, backupCount=5, encoding='utf-8')
    fh.namer = lambda x: "backup." + x.split(".")[-1]

    fmt = logging.Formatter("%(asctime)s %(levelname)s %(funcName)s：%(lineno)d  %(pathname)s  %(message)s")  # 日志输出格式
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger

