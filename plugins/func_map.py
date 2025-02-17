#为func_calling提供函数映射
import importlib
import inspect
import json

from developTools.utils.logger import get_logger

logger=get_logger()
dynamic_imports = {
    "run.basic_plugin": [
        "call_weather_query", "call_setu", "call_image_search",
        "call_tts", "call_tarot", "call_pick_music",
        "call_fortune", "call_all_speakers"
    ],
    "run.user_data": [
        "call_user_data_register", "call_user_data_query", "call_user_data_sign",
        "call_change_city", "call_change_name", "call_permit",
        "call_delete_user_history", "call_clear_all_history"
    ],
    "run.groupManager.self_Manager": [
        "call_operate_blandwhite", "garbage_collection",
        "report_to_master", "send", "send_contract"
    ],
    "run.groupManager.nailong_get": ["operate_group_censor"],
    "run.resource_search.resource_search": [
        "search_book_info", "call_asmr", "call_download_book"
    ],
    "run.acg_infromation.bangumi": ["call_bangumi_search"],
    "run.acg_infromation.character_identify": ["call_character_identify"],
    "run.streaming_media.youtube": ["download_youtube"],
    "run.streaming_media.link_parsing": ["call_bili_download_video"],
    "run.aiDraw": ["call_text2img", "call_aiArtModerate"],
    "run.scheduledTasks": ["operate_group_push_tasks"],
    "run.resource_search.engine_search": ["search_net", "read_html"]
}

# 存储成功加载的函数
loaded_functions = {}


# 动态导入模块和函数
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

    # 检查是否为异步函数
    if not inspect.iscoroutinefunction(func):
        raise TypeError(f"'{func_name}' is not an async function.")

    # 调用函数并传入参数
    return await func(bot, event, config, **params)
