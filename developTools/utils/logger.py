import logging
import os
from datetime import datetime
import colorlog

# 全局变量，用于存储 logger 实例和屏蔽的日志类别
_logger = None
_blocked_loggers = ["INFO_MSG"]


def createLogger(blocked_loggers=None):
    global _logger, _blocked_loggers
    if blocked_loggers is not None:
        _blocked_loggers = blocked_loggers

    # 确保日志文件夹存在
    log_folder = "log"
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    # 创建一个 logger 对象
    logger = logging.getLogger("Eridanus")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False  # 防止重复日志

    # 自定义过滤器，用于屏蔽指定的日志类别
    class BlockLoggerFilter(logging.Filter):
        def filter(self, record):
            if record.levelname in _blocked_loggers:
                return False
            return True

    # 设置控制台日志格式和颜色
    console_handler = logging.StreamHandler()
    console_format = '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - [bot] %(message)s'
    console_colors = {
        'DEBUG': 'white',
        'INFO': 'cyan',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
    console_formatter = colorlog.ColoredFormatter(console_format, log_colors=console_colors)
    console_handler.setFormatter(console_formatter)
    console_handler.addFilter(BlockLoggerFilter())
    logger.addHandler(console_handler)

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

    console_formatter_msg = colorlog.ColoredFormatter(console_format_msg, log_colors=console_colors_msg)
    console_formatter_func = colorlog.ColoredFormatter(console_format_func, log_colors=console_colors_func)
    console_formatter_server = colorlog.ColoredFormatter(console_format_server, log_colors=console_colors_server)

    # 设置文件日志格式
    file_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    file_formatter = logging.Formatter(file_format)

    # 获取当前日期
    current_date = datetime.now().strftime("%Y-%m-%d")
    log_file_path = os.path.join(log_folder, f"{current_date}.log")

    # 创建文件处理器
    file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8')
    file_handler.setFormatter(file_formatter)
    file_handler.addFilter(BlockLoggerFilter())
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
            file_handler.addFilter(BlockLoggerFilter())
            logger.addHandler(file_handler)

    # 在 logger 上绑定更新日志文件的函数
    logger.update_log_file = update_log_file

    # --- 添加区分消息、功能和服务器的函数 ---
    def info_msg(self, message, *args, **kwargs):
        if self.isEnabledFor(logging.INFO) and "INFO_MSG" not in _blocked_loggers:
            console_handler.setFormatter(console_formatter_msg)
            self._log(logging.INFO, message, args, **kwargs)
            console_handler.setFormatter(console_formatter)

    def info_func(self, message, *args, **kwargs):
        if self.isEnabledFor(logging.INFO) and "INFO_FUNC" not in _blocked_loggers:
            console_handler.setFormatter(console_formatter_func)
            self._log(logging.INFO, message, args, **kwargs)
            console_handler.setFormatter(console_formatter)

    def server(self, message, *args, **kwargs):
        if self.isEnabledFor(logging.INFO) and "SERVER" not in _blocked_loggers:
            console_handler.setFormatter(console_formatter_server)
            self._log(logging.INFO, message, args, **kwargs)
            console_handler.setFormatter(console_formatter)

    # 将新函数绑定到 logger 类
    logging.Logger.info_msg = info_msg
    logging.Logger.info_func = info_func
    logging.Logger.server = server
    # --- 结束添加区分消息、功能和服务器的函数 ---

    _logger = logger


def get_logger(blocked_loggers=None):
    global _logger
    if _logger is None:
        createLogger(blocked_loggers)
    _logger.update_log_file()
    return _logger


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