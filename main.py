import concurrent.futures
import copy
import importlib
import os
import sys
import asyncio
import threading
import traceback

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from plugins.core.yamlLoader import YAMLManager
if sys.platform == 'win32':
  asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
from plugins.utils.websocket_fix import ExtendBot

config = YAMLManager(["config/settings.yaml",
                      "config/basic_config.yaml",
                      "config/api.yaml",
                      "config/controller.yaml",
                      "data/censor/censor_group.yaml",
                      "data/censor/censor_user.yaml",
                      "data/media_service/bilibili/bili_dynamic.yaml",
                      "data/tasks/scheduledTasks.yaml",
                      "data/tasks/scheduledTasks_push_groups.yaml",
                      "data/recognize/doro.yaml",
                      "data/recognize/nailong.yaml",]) #这玩意用来动态加载和修改配置文件
#from developTools.adapters.http_adapter import HTTPBot
#bot = HTTPBot(http_sever=config.basic_config["adapter"]["http_client"]["url"],access_token=config.basic_config["adapter"]["access_token"],host=str(config.basic_config['adapter']["http_sever"]["host"]), port=int(config.basic_config["adapter"]["http_sever"]["port"]))
#或者使用ws适配器
bot1 = ExtendBot(config.basic_config["adapter"]["ws_client"]["ws_link"],config,blocked_loggers=["DEBUG", "INFO_MSG"])
if config.basic_config["webui"]:
    bot2 = ExtendBot("ws://127.0.0.1:5008", config,
                     blocked_loggers=["DEBUG", "INFO_MSG","warning"])
#插件列表
plugin_modules = [
    #基础功能？
    ("aiDraw", "run.aiDraw"),
    ("aiReply", "run.aiReply"),
    ("basic_plugin", "run.basic_plugin"),

    ("user_data", "run.user_data"),
    ("api_implements", "run.api_implements"),
    ("Mface_Record","run.system_plugin.Mface_Record"),
    #群管/自管
    ("self_Manager", "run.groupManager.self_Manager"),
    ("group_manager", "run.groupManager.group_manager"),
    ("word_cloud", "run.groupManager.word_cloud"),
    ("wifeyouwant", "run.groupManager.wifeyouwant"),
    #acg信息
    ("galgame", "run.acg_infromation.galgame"),
    ("bangumi", "run.acg_infromation.bangumi"),
    ("character_identify", "run.acg_infromation.character_identify"),
    #流媒体相关
    ("youtube", "run.streaming_media.youtube"),
    ("bilibili", "run.streaming_media.bilibili"),
    ("Link_parsing", "run.streaming_media.Link_parsing"),
    ("iwara", "run.streaming_media.iwara"),
    #资源搜索
    ("resource_search", "run.resource_search.resource_search"),
    ("engine_search", "run.resource_search.engine_search"),
    #游戏服务
    ("blue_archive", "run.anime_game_service.blue_archive"),
    ("steam_service", "run.anime_game_service.steam_service"),


]

def safe_import_and_load(plugin_name, module_path,bot,config):
    try:
        module = importlib.import_module(module_path)
        if hasattr(module, "main"):
            module.main(bot, config)
            bot.logger.info(f"✅ 成功加载插件：{plugin_name}")
        else:
            bot.logger.warning(f"⚠️ 插件{module_path} {plugin_name} 缺少 `main()` 方法")
    except Exception as e:
        bot.logger.warning(f"❌ 插件 {plugin_name} 加载失败：{e}")
        traceback.print_exc()
        bot.logger.warning(f"❌ 建议执行一次 更新脚本(windows)/tool.py(linux) 自动补全依赖后重启以尝试修复此问题")
        bot.logger.warning(f"❌ 如仍无法解决，请反馈此问题至 https://github.com/avilliai/Eridanus/issues 或我们的QQ群 913122269")
def load_plugins(bot,config):
    # 并行加载插件
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(safe_import_and_load, name, path,bot,config): name for name, path in plugin_modules
        }
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                bot.logger.warning(f"❌ 插件 {futures[future]} 加载过程中发生异常：{e}")

    # 奶龙检测（可选功能）
    try:
        if config.settings["抽象检测"]["奶龙检测"] or config.settings["抽象检测"]["doro检测"]:
            safe_import_and_load("nailong_get", "run.groupManager.nailong_get", bot, config)

    except Exception as e:
        bot.logger.warning("⚠️ 【可选功能】奶龙检测相关依赖未安装，如有需要，请安装 AI 检测必要素材")
try:
  enable_webui=config.basic_config["webui"]
except:
  enable_webui=False
if enable_webui and os.path.exists("../server.exe"):
    config_copy = YAMLManager(["config/settings.yaml",
                          "config/basic_config.yaml",
                          "config/api.yaml",
                          "config/controller.yaml",
                          "data/censor/censor_group.yaml",
                          "data/censor/censor_user.yaml",
                          "data/media_service/bilibili/bili_dynamic.yaml",
                          "data/tasks/scheduledTasks.yaml",
                          "data/tasks/scheduledTasks_push_groups.yaml",
                          "data/recognize/doro.yaml",
                          "data/recognize/nailong.yaml", ])  # 这玩意用来动态加载和修改配置文件
    def config_fix(config_copy):
        config_copy.settings["JMComic"]["anti_nsfw"] = "no_censor"
        config_copy.settings["asmr"]["gray_layer"] = False
        config_copy.settings["basic_plugin"]["setu"]["gray_layer"] = False
        config_copy.api["llm"]["读取群聊上下文"]=False
    def run_bot2():
        """在独立线程运行 bot2"""
        config_fix(config_copy)
        load_plugins(bot2,config_copy)
        bot2.run()


    bot2_thread = threading.Thread(target=run_bot2, daemon=True)
    bot2_thread.start()
load_plugins(bot1,config)
bot1.run()



