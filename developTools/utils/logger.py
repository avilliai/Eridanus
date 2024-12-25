import logging
import os
from datetime import datetime
import colorlog


def createLogger():
    # 确保日志文件夹存在
    log_folder = "log"
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    # 创建一个 logger 对象
    logger = logging.getLogger("Eridanus")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False  # 防止重复日志

    # 设置控制台日志格式和颜色
    console_handler = logging.StreamHandler()
    console_format = '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    console_colors = {
        'DEBUG': 'white',
        'INFO': 'cyan',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
    console_formatter = colorlog.ColoredFormatter(console_format, log_colors=console_colors)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # 设置文件日志格式
    file_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    file_formatter = logging.Formatter(file_format)

    # 获取当前日期
    current_date = datetime.now().strftime("%Y-%m-%d")
    log_file_path = os.path.join(log_folder, f"{current_date}.log")

    # 创建文件处理器
    file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # 定义一个函数来更新日志文件（按日期切换）
    def update_log_file():
        nonlocal log_file_path, file_handler
        new_date = datetime.now().strftime("%Y-%m-%d")
        new_log_file_path = os.path.join(log_folder, f"{new_date}.log")
        if new_log_file_path != log_file_path:
            logger.removeHandler(file_handler)
            file_handler.close()
            log_file_path = new_log_file_path
            file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8')
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

    # 在 logger 上绑定更新日志文件的函数
    logger.update_log_file = update_log_file

    return logger


# 创建 logger 实例
logger = createLogger()


def get_logger():
    # 每次获取 logger 时检查是否需要更新日志文件
    logger.update_log_file()
    return logger
