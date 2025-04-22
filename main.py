import concurrent.futures
import importlib
import os
import sys
import asyncio
import threading
import traceback

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from framework_common.framework_util.yamlLoader import YAMLManager
if sys.platform == 'win32':
  asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
from framework_common.framework_util.websocket_fix import ExtendBot

config = YAMLManager("run") #这玩意用来动态加载和修改配置文件
#from developTools.adapters.http_adapter import HTTPBot
#bot = HTTPBot(http_sever=config.basic_config["adapter"]["http_client"]["url"],access_token=config.basic_config["adapter"]["access_token"],host=str(config.basic_config['adapter']["http_sever"]["host"]), port=int(config.basic_config["adapter"]["http_sever"]["port"]))
#或者使用ws适配器
bot1 = ExtendBot(config.common_config.basic_config["adapter"]["ws_client"]["ws_link"],config,blocked_loggers=["DEBUG", "INFO_MSG"])
if config.common_config.basic_config["webui"]:
    bot2 = ExtendBot("ws://127.0.0.1:5008", config,
                     blocked_loggers=["DEBUG", "INFO_MSG","warning"])

PLUGIN_DIR = "run"
def find_plugins(plugin_dir=PLUGIN_DIR):
    plugin_modules = []
    for root, _, files in os.walk(plugin_dir):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                module_path = os.path.join(root, file)
                module_name = module_path.replace(os.sep, ".").removesuffix(".py")
                plugin_name = os.path.splitext(file)[0]
                if check_has_main(module_name) and plugin_name!="nailong_get":
                    plugin_modules.append((plugin_name, module_name))
                else:
                    if plugin_name!="nailong_get" and plugin_name!="func_collection" and f"service" not in module_name:
                        bot1.logger.info(f"⚠️ The plugin `{module_path} {plugin_name}` does not have a main() method. If this plugin is a function collection, please ignore this warning.")

    return plugin_modules

def check_has_main(module_name):
    """检查模块是否包含 `main()` 方法"""
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            bot1.logger.warning(f"⚠️ 未找到模块 {module_name}")
            return False
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return hasattr(module, "main")
    except Exception:
        bot1.logger.warning(f"⚠️ 加载模块 {module_name} 失败，请尝试补全依赖后重试")
        traceback.print_exc()
        return False


# 自动构建插件列表
plugin_modules = find_plugins()
bot1.logger.info(f"🔧 共读取到插件：{len(plugin_modules)}个")
bot1.logger.info(f"🔧 正在加载插件....") #{', '.join(name for name, _ in plugin_modules)}")

def safe_import_and_load(plugin_name, module_path,bot,config):
    try:
        module = importlib.import_module(module_path)
        if ".service." not in str(module_path):
            if hasattr(module, "main") and ".service." not in str(module_path):
                module.main(bot, config)
                bot.logger.info(f"✅ 成功加载插件：{plugin_name}")
            else:
                bot.logger.warning(f"⚠️ 插件{module_path} {plugin_name} 缺少 `main()` 方法")
    except Exception as e:
        bot.logger.warning(f"❌ 插件{module_path} {plugin_name} 加载失败：{e}")
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
    config_copy = YAMLManager("run") # 这玩意用来动态加载和修改配置文件
    def config_fix(config_copy):
        config_copy.config.settings["JMComic"]["anti_nsfw"] = "no_censor"
        config_copy.config.settings["asmr"]["gray_layer"] = False
        config_copy.config.settings["basic_plugin"]["setu"]["gray_layer"] = False
        config_copy.ai_llm.config["llm"]["读取群聊上下文"]=False
        config_copy.config.basic_config["master"]["id"]=111111111
    def run_bot2():
        """在独立线程运行 bot2"""
        config_fix(config_copy)
        load_plugins(bot2,config_copy)
        bot2.run()


    bot2_thread = threading.Thread(target=run_bot2, daemon=True)
    bot2_thread.start()
load_plugins(bot1,config)
bot1.run()



