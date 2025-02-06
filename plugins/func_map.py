#为func_calling提供函数映射
import inspect
import json

from run.basic_plugin import call_weather_query,call_setu,call_image_search,call_tts,call_tarot,call_pick_music,call_fortune,call_all_speakers
from run.user_data import call_user_data_register,call_user_data_query,call_user_data_sign,call_change_city,call_change_name,call_permit
from run.groupManager.self_Manager import call_operate_blandwhite,garbage_collection,report_to_master,send,send_contract
from run.groupManager.nailong_get import operate_group_censor
from run.resource_search.resource_search import search_book_info,call_asmr,call_download_book
from run.user_data import call_delete_user_history,call_clear_all_history
from run.acg_infromation.bangumi import call_bangumi_search
from run.streaming_media.youtube import download_youtube
from run.aiDraw import call_text2img,call_aiArtModerate
from run.scheduledTasks import operate_group_push_tasks
from run.resource_search.engine_search import search_net

async def call_quit_chat(bot,event,config):
    return False

async def call_func(bot,event,config,func_name, params):

    """
    动态调用已导入的函数。

    参数:
        func_name (str): 函数名。
        params (str): JSON 字符串，包含函数参数。

    返回:
        异步函数的返回值。
    """
    print(f"Calling function '{func_name}' with parameters: {params}")
    # 从全局作用域中获取函数对象
    func = globals().get(func_name)

    if func is None:
        raise ValueError(f"Function '{func_name}' not found.")

    # 检查是否为可调用对象
    if not callable(func):
        raise TypeError(f"'{func_name}' is not callable.")

    # 检查是否为异步函数
    if not inspect.iscoroutinefunction(func):
        raise TypeError(f"'{func_name}' is not an async function.")

    # 将 JSON 字符串解析为字典


    # 调用函数并传入参数
    return await func(bot,event,config,**params)
