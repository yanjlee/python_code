# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1..0.0
# -=-=-=-=-=-=-=-=-=-=-=

import logging as log
import os
import time

def logger():
    BASE_DIR = os.path.dirname(__file__)
    LOG_PATH = BASE_DIR + '/'
    LOG_FILENAME = 'CIGRG_001_' + str(time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time()))) + '.log'

    # 创建一个logger
    logger = log.getLogger('my_log')
    logger.setLevel(log.DEBUG)

    # 创建一个handler，用于写入日志文件
    output_file = log.FileHandler(LOG_PATH + LOG_FILENAME)
    output_file.setLevel(log.DEBUG)

    # 再创建一个handler，用于输出到控制台
    console_info = log.StreamHandler()
    console_info.setLevel(log.DEBUG)

    # 定义handler的输出格式
    formatter = log.Formatter('[%(asctime)s][%(filename)s][%(levelname)s] ## %(message)s')
    output_file.setFormatter(formatter)
    console_info.setFormatter(formatter)

    # 给logger添加handler
    logger.addHandler(output_file)
    logger.addHandler(console_info)