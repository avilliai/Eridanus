import logging
import os
from datetime import datetime
from logging import Logger

import colorlog


class ErLogger(Logger):
    _logger = None
    _blocked_loggers = ["INFO_MSG"]
    _blocked_logger_filter = logging.Filter

    # 定义一个函数来更新日志文件（按日期切换）

    def __init__(self, name: str):
        super().__init__(name)
        self.name = name
        self.log_folder = 'log'
        self._blocked_logger_filter.filter = lambda self_, record: not record.levelname in self._blocked_loggers

    def get_logger(self, blocked_loggers=None) -> Logger:
        if self._logger is None:
            self.createLogger(blocked_loggers)
        self.update_log_file()
        return self._logger

    def update_log_file(self):
        new_date = datetime.now().strftime("%Y-%m-%d")
        new_log_file_path = os.path.join(self.log_folder, f"{new_date}.log")
        if new_log_file_path != self.log_file_path:
            logger.removeHandler(self.file_handler)
            self.file_handler.close()
            self.log_file_path = new_log_file_path
            file_handler = logging.FileHandler(self.log_file_path, mode='a', encoding='utf-8')
            file_handler.setFormatter(self.file_formatter)
            file_handler.addFilter(self._blocked_logger_filter())
            logger.addHandler(file_handler)

    def createLogger(self, blocked_loggers=None):
        _blocked_loggers = self._blocked_loggers or blocked_loggers

        # 确保日志文件夹存在
        if not os.path.exists(self.log_folder):
            os.makedirs(self.log_folder)

        # 创建一个 logger 对象
        logger = logging.getLogger("Eridanus")
        logger.setLevel(logging.DEBUG)
        logger.propagate = False  # 防止重复日志

        # 设置控制台日志格式和颜色
        self.console_handler = logging.StreamHandler()
        console_format = '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - [bot] %(message)s'
        console_colors = {
            'DEBUG': 'white',
            'INFO': 'cyan',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }
        self.console_formatter = colorlog.ColoredFormatter(console_format, log_colors=console_colors)
        self.console_handler.setFormatter(self.console_formatter)
        self.console_handler.addFilter(self._blocked_logger_filter())
        logger.addHandler(self.console_handler)

        # --- 增加颜色区分消息、功能和服务器 ---
        console_format_msg = '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - [MSG] %(message)s'
        console_format_func = '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - [FUNC] %(message)s'
        console_format_server = '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - [SERVER] %(message)s'

        console_colors_msg = {
            'DEBUG': 'white',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }
        console_colors_func = {
            'DEBUG': 'white',
            'INFO': 'blue',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }
        console_colors_server = {
            'DEBUG': 'white',
            'INFO': 'purple',  # 使用紫色代替粉红色（colorlog 不支持直接的 pink，但 purple 接近）
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }

        self.console_formatter_msg = colorlog.ColoredFormatter(console_format_msg, log_colors=console_colors_msg)
        self.console_formatter_func = colorlog.ColoredFormatter(console_format_func, log_colors=console_colors_func)
        self.console_formatter_server = colorlog.ColoredFormatter(console_format_server, log_colors=console_colors_server)

        # 设置文件日志格式
        file_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        self.file_formatter = logging.Formatter(file_format)

        # 获取当前日期
        current_date = datetime.now().strftime("%Y-%m-%d")
        self.log_file_path = os.path.join(self.log_folder, f"{current_date}.log")

        # 创建文件处理器
        self.file_handler = logging.FileHandler(self.log_file_path, mode='a', encoding='utf-8')
        self.file_handler.setFormatter(self.file_formatter)
        self.file_handler.addFilter(self._blocked_logger_filter())
        logger.addHandler(self.file_handler)
        # 在 logger 上绑定更新日志文件的函数
        logger.update_log_file = self.update_log_file
        # 将新函数绑定到 logger 类
        logging.Logger.info_msg = self.info_msg
        logging.Logger.info_func = self.info_func
        logging.Logger.server = self.server
        # --- 结束添加区分消息、功能和服务器的函数 ---

        self._logger = logger

        # --- 添加区分消息、功能和服务器的函数 ---

    def info_msg(self, message, *args, **kwargs):
        if self.isEnabledFor(logging.INFO) and "INFO_MSG" not in self._blocked_loggers:
            self.console_handler.setFormatter(self.console_formatter_msg)
            self._log(logging.INFO, message, args, **kwargs)
            self.console_handler.setFormatter(self.console_formatter)

    def info_func(self, message, *args, **kwargs):
        if self.isEnabledFor(logging.INFO) and "INFO_FUNC" not in self._blocked_loggers:
            self.console_handler.setFormatter(self.console_formatter_func)
            self._log(logging.INFO, message, args, **kwargs)
            self.console_handler.setFormatter(self.console_formatter)

    def server(self, message, *args, **kwargs):
        if self.isEnabledFor(logging.INFO) and "SERVER" not in self._blocked_loggers:
            self.console_handler.setFormatter(self.console_formatter_server)
            self._log(logging.INFO, message, args, **kwargs)
            self.console_handler.setFormatter(self.console_formatter)


er_logger = ErLogger("Er")
get_logger = er_logger.get_logger

# 使用示例
if __name__ == "__main__":
    # 精确屏蔽 INFO_MSG 和 DEBUG 类型日志
    logger = get_logger(blocked_loggers=["INFO_MSG"])
    logger.debug("This is a debug message.")  # 不会显示
    logger.info("This is an info message.")  # 会显示
    logger.warning("This is a warning message.")  # 会显示
    logger.error("This is an error message.")  # 会显示
    logger.critical("This is a critical message.")  # 会显示

    logger.info_msg("This is a server message.")  # 不会显示
    logger.info_func("This is a function info.")  # 会显示
    logger.server("This is a server-specific message.")  # 会显示（紫色）

    logger2 = get_logger()
    print(f"logger == logger2: {logger == logger2}")
