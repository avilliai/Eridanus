import concurrent.futures
import importlib
import os
import sys
import asyncio
import threading
import traceback

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from framework_common.framework_util.yamlLoader import YAMLManager
from framework_common.framework_util.websocket_fix import ExtendBot

config = YAMLManager("run")  # 这玩意用来动态加载和修改配置文件
bot1 = ExtendBot(config.common_config.basic_config["adapter"]["ws_client"]["ws_link"], config,
                 blocked_loggers=["DEBUG", "INFO_MSG"])

bot1.logger.info("正在初始化....")
if config.common_config.basic_config["webui"]["enable"]:
    bot2 = ExtendBot("ws://127.0.0.1:5007/api/ws", config, blocked_loggers=["DEBUG", "INFO_MSG", "warning"])
    bot1.logger.server("🔧 WebUI 服务启动中，请在完全启动后，本机浏览器访问 http://localhost:5007")
    bot1.logger.server("🔧 若您部署的远程主机有公网ip或端口转发功能，请访问对应ip的5007端口，或设置的转发端口。")
    bot1.logger.server("🔧 WebUI 初始账号密码均为 eridanus")
    bot1.logger.server("🔧 WebUI 初始账号密码均为 eridanus")
    bot1.logger.server("🔧 WebUI 初始账号密码均为 eridanus")
    webui_dir = os.path.abspath(os.getcwd() + "/web")
    sys.path.append(webui_dir)


    def run_webui():
        """在子线程中运行 WebUI，隔离模块加载路径"""
        try:
            # 确保 WebUI 模块可以从 webui_dir 加载
            bot1.logger.info(f"WebUI 线程：启动 WebUI，模块路径 {webui_dir}")
            from web.server_new import start_webui
            start_webui()
        except Exception as e:
            bot1.logger.error(f"WebUI 线程：启动 WebUI 失败：{e}")
            traceback.print_exc()


    external_cwd = os.getcwd()
    bot1.logger.info(f"主线程：外部程序运行在 {external_cwd}")

    # 在子线程中启动 WebUI
    webui_thread = threading.Thread(target=run_webui, daemon=True)
    webui_thread.start()
    bot1.logger.info("主线程：WebUI 已启动在子线程中")


PLUGIN_DIR = "run"
# 创建模块缓存字典
module_cache = {}


def check_has_main_and_cache(module_name):
    """检查模块是否包含 `main()` 方法，并缓存已加载的模块"""
    global module_cache

    try:
        if module_name in module_cache:
            module = module_cache[module_name]
        else:
            spec = importlib.util.find_spec(module_name)
            if spec is None:
                bot1.logger.warning(f"⚠️ 未找到模块 {module_name}")
                return False, None

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            # 缓存模块
            module_cache[module_name] = module

        return hasattr(module, "main"), module
    except Exception as e:
        if not module_name.startswith("run.character_detection."):
            bot1.logger.warning(f"⚠️ 加载模块 {module_name} 失败，请尝试补全依赖后重试")
            traceback.print_exc()
        return False, None
def find_plugins(plugin_dir=PLUGIN_DIR):
    plugin_modules = []
    for root, _, files in os.walk(plugin_dir):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                module_path = os.path.join(root, file)
                module_name = module_path.replace(os.sep, ".").removesuffix(".py")
                plugin_name = os.path.splitext(file)[0]

                has_main, module = check_has_main_and_cache(module_name)

                if has_main and plugin_name != "nailong_get":
                    plugin_modules.append((plugin_name, module_name, module))
                else:
                    if plugin_name != "nailong_get" and plugin_name != "func_collection" and f"service" not in module_name:
                        bot1.logger.warning(
                            f"⚠️ The plugin `{module_path} {plugin_name}` does not have a main() method. If this plugin is a function collection, please ignore this warning.")

    return plugin_modules
# 自动构建插件列表
plugin_modules = find_plugins()
bot1.logger.info(f"🔧 共读取到插件：{len(plugin_modules)}个")
bot1.logger.info(f"🔧 正在加载插件....")
def safe_import_and_load(plugin_name, module_path, cached_module, bot, config):
    try:
        # 使用缓存的模块而不是重新导入
        module = cached_module

        if ".service." not in str(module_path):
            if hasattr(module, "main"):
                module.main(bot, config)
                bot.logger.info(f"✅ 成功加载插件：{plugin_name}")
            else:
                bot.logger.warning(f"⚠️ 插件{module_path} {plugin_name} 缺少 `main()` 方法")
    except Exception as e:
        bot.logger.warning(f"❌ 插件{module_path} {plugin_name} 加载失败：{e}")
        traceback.print_exc()
        bot.logger.warning(f"❌ 建议执行一次 更新脚本(windows)/tool.py(linux) 自动补全依赖后重启以尝试修复此问题")
        bot.logger.warning(
            f"❌ 如仍无法解决，请反馈此问题至 https://github.com/avilliai/Eridanus/issues 或我们的QQ群 913122269")

def load_plugins(bot, config):
    # 并行加载插件
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(safe_import_and_load, name, path, module, bot, config): name
            for name, path, module in plugin_modules
        }
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                bot.logger.warning(f"❌ 插件 {futures[future]} 加载过程中发生异常：{e}")

    # 奶龙检测（可选功能）
    try:
        if config.character_detection.config["抽象检测"]["奶龙检测"] or config.character_detection.config["抽象检测"][
            "doro检测"]:
            # 这里也可以优化，检查缓存中是否已有此模块
            if "run.character_detection.nailong_get" in module_cache:
                module = module_cache["run.character_detection.nailong_get"]
                safe_import_and_load("nailong_get", "run.character_detection.nailong_get", module, bot, config)
            else:
                module = importlib.import_module("run.character_detection.nailong_get")
                module_cache["run.character_detection.nailong_get"] = module
                safe_import_and_load("nailong_get", "run.character_detection.nailong_get", module, bot, config)

    except Exception as e:
        bot.logger.warning("⚠️ 【可选功能】奶龙检测相关依赖未安装，如有需要，请安装 AI 检测必要素材")

def webui_bot():
    config_copy = YAMLManager("run")  # 这玩意用来动态加载和修改配置文件
    def config_fix(config_copy):
        config_copy.resource_collector.config["JMComic"]["anti_nsfw"] = "no_censor"
        config_copy.resource_collector.config["asmr"]["gray_layer"] = False
        config_copy.basic_plugin.config["setu"]["gray_layer"] = False
        config_copy.resource_collector.config["iwara"]["iwara_gray_layer"] = False
        config_copy.ai_llm.config["llm"]["读取群聊上下文"] = False
        config_copy.resource_collector.config["iwara"]["zip_file"] = False
        config_copy.common_config.basic_config["master"]["id"] = 111111111
    def run_bot2():
        """在独立线程运行 bot2"""
        config_fix(config_copy)
        load_plugins(bot2, config_copy)
        bot2.run()

    bot2_thread = threading.Thread(target=run_bot2, daemon=True)
    bot2_thread.start()

if config.common_config.basic_config["webui"]["enable"]:
    webui_bot()
load_plugins(bot1, config)
bot1.run()