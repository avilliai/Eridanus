# __init__.py
from .common import printf,printf_check,random_str
from .download_img import download_img


# 定义 __all__ 列表，明确导出的内容
__all__ = ["printf",'printf_check','random_str','download_img']