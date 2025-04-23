#为func_calling提供函数映射
import importlib
import inspect
import json
import os
import traceback

from developTools.utils.logger import get_logger

logger=get_logger()
PLUGIN_DIR = "run"
dynamic_imports = {}

for root, dirs, files in os.walk(PLUGIN_DIR):
    # 检查路径中是否包含 service 文件夹
    if "service" in root.split(os.sep):
        continue

    if "__init__.py" in files:
        module_name = root.replace(os.sep, ".")
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, "dynamic_imports"):
                dynamic_imports.update(module.dynamic_imports)
                logger.info(f"✅ 函数调用映射加载成功: {module_name}.dynamic_imports")
            else:
                logger.warning(f"⚠️ {module_name} 未定义 dynamic_imports")
        except Exception as e:
            logger.error(f"❌ 无法导入 {module_name}: {e}")
            traceback.print_exc()

loaded_functions = {}


# 动态导入
for module_name, functions in dynamic_imports.items():
    try:
        module = importlib.import_module(module_name)  # 动态导入模块
        for func in functions:
            if hasattr(module, func):
                loaded_functions[func] = getattr(module, func)  # 存入字典
                #logger.info(f"✅ 成功加载 {module_name}.{func}")
            else:
                logger.warning(f"⚠️ {module_name} 中不存在 {func}")
    except Exception as e:
        logger.error(f"❌ 无法导入模块 {module_name}: {e}")
        traceback.print_exc()

async def call_quit_chat(bot, event, config):
    return False

async def call_func(bot, event, config, func_name, params):
    """
    动态调用已导入的函数。

    参数:
        func_name (str): 函数名。
        params (dict): 函数参数字典。

    返回:
        异步函数的返回值。
    """
    print(f"Calling function '{func_name}' with parameters: {params}")

    # **改成从 `loaded_functions` 获取函数**
    func = loaded_functions.get(func_name)

    if func is None:
        raise ValueError(f"Function '{func_name}' not found in loaded_functions.")

    # 检查是否为可调用对象
    if not callable(func):
        raise TypeError(f"'{func_name}' is not callable.")


    if not inspect.iscoroutinefunction(func):
        raise TypeError(f"'{func_name}' is not an async function.")

    # 调用函数并传入参数
    return await func(bot, event, config, **params)
