import asyncio
import os
import sys
import signal
import logging
import threading
import io

logger = logging.getLogger(__name__)

current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)
sys.path.append(current_dir)
from framework_common.utils.install_and_import import install_and_import
psutil=install_and_import("psutil")

try:
    from framework_common.framework_util.yamlLoader import YAMLManager
    from framework_common.framework_util.websocket_fix import ExtendBot
    from developTools.event.events import GroupMessageEvent
except ImportError as e:
    sys.stderr.write(f"错误：无法导入必要的模块: {e}\n")
    sys.stderr.write("请确保 framework_common 和 developTools 在 Python 路径中，或者与 launch.py 结构正确\n")
    sys.exit(1)

PYTHON_EXECUTABLE = sys.executable
MAIN_SCRIPT_PATH = os.path.join(current_dir, "main.py")

main_py_process_info = {
    "process": None,
    "stdout_task": None,
    "stderr_task": None
}

main_event_loop = None
config_manager_instance = None

async def _read_stream(stream):
    while True:
        try:
            line = await stream.readline()
            if line:
                decoded_line = line.decode('utf-8', errors='replace').strip()
                logger.info(f"{decoded_line}")
            else:
                break
        except Exception as e:
            logger.error(f"读取流时发生错误: {e}")
            break

async def start_main_py():
    global main_py_process_info
    if main_py_process_info["process"] and main_py_process_info["process"].returncode is None:
        logger.warning("main.py 似乎已在运行")
        return

    logger.info(f"正在启动: {PYTHON_EXECUTABLE} {MAIN_SCRIPT_PATH}")
    try:
        process = await asyncio.create_subprocess_exec(
            PYTHON_EXECUTABLE, MAIN_SCRIPT_PATH,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=current_dir,
            env=dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONUTF8='1')
        )
        main_py_process_info["process"] = process
        logger.info(f"main.py 已启动，PID: {process.pid}")

        main_py_process_info["stdout_task"] = asyncio.create_task(
            _read_stream(process.stdout)
        )
        main_py_process_info["stderr_task"] = asyncio.create_task(
            _read_stream(process.stderr)
        )
    except Exception as e:
        logger.error(f"启动 main.py 失败: {e}", exc_info=True)
        main_py_process_info["process"] = None


async def stop_main_py():
    global main_py_process_info
    proc_obj = main_py_process_info["process"]
    if not proc_obj or proc_obj.returncode is not None:
        logger.info("main.py 未运行或已停止")
        if main_py_process_info["stdout_task"] and not main_py_process_info["stdout_task"].done():
            main_py_process_info["stdout_task"].cancel()
        if main_py_process_info["stderr_task"] and not main_py_process_info["stderr_task"].done():
            main_py_process_info["stderr_task"].cancel()
        main_py_process_info = {"process": None, "stdout_task": None, "stderr_task": None}
        return

    pid_to_stop = proc_obj.pid
    logger.info(f"正在尝试停止 main.py (PID: {pid_to_stop}) 及其子进程...")
    try:
        parent = psutil.Process(pid_to_stop)
        children = parent.children(recursive=True)
        for child in children:
            logger.info(f"正在终止子进程 PID: {child.pid}")
            try: child.terminate()
            except psutil.NoSuchProcess: pass
        
        gone, alive = psutil.wait_procs(children, timeout=3)
        for p in alive:
            logger.warning(f"子进程 PID: {p.pid} 未能在3秒内终止，将强制结束")
            try: p.kill()
            except psutil.NoSuchProcess: pass

        logger.info(f"正在终止主进程 PID: {parent.pid}")
        try:
            parent.terminate()
            await proc_obj.wait()
        except psutil.NoSuchProcess: pass
        except ProcessLookupError: pass

        logger.info(f"main.py (PID: {pid_to_stop}) 已发送终止信号")
    except psutil.NoSuchProcess:
        logger.warning(f"尝试停止时未找到 main.py 进程 (PID: {pid_to_stop})，可能已经停止")
    except Exception as e:
        logger.error(f"停止 main.py 时发生错误: {e}", exc_info=True)
    finally:
        if main_py_process_info["stdout_task"] and not main_py_process_info["stdout_task"].done():
            main_py_process_info["stdout_task"].cancel()
        if main_py_process_info["stderr_task"] and not main_py_process_info["stderr_task"].done():
            main_py_process_info["stderr_task"].cancel()
        try:
            if main_py_process_info["stdout_task"]: await asyncio.wait_for(main_py_process_info["stdout_task"], timeout=1)
        except (asyncio.CancelledError, asyncio.TimeoutError): pass
        except Exception as e_task_stdout: logger.debug(f"Exception during stdout_task cleanup: {e_task_stdout}")

        try:
            if main_py_process_info["stderr_task"]: await asyncio.wait_for(main_py_process_info["stderr_task"], timeout=1)
        except (asyncio.CancelledError, asyncio.TimeoutError): pass
        except Exception as e_task_stderr: logger.debug(f"Exception during stderr_task cleanup: {e_task_stderr}")

        main_py_process_info = {"process": None, "stdout_task": None, "stderr_task": None}


async def actual_restart_task():
    logger.info("[MainLoop] 接收到重启任务，正在执行...")
    await stop_main_py()
    await asyncio.sleep(3) # 释放资源的
    await start_main_py()
    logger.info("[MainLoop] main.py 重启流程完毕")


def bot_thread_function(loop_for_scheduler, global_cfg_manager):
    logger.info("[BotThread] 机器人线程已启动")
    bot_instance_for_thread = None

    try:
        ws_link = global_cfg_manager.common_config.basic_config["adapter"]["ws_client"]["ws_link"]
        master_id = str(global_cfg_manager.common_config.basic_config["master"]["id"])

        from developTools.adapters.websocket_adapter import WebSocketBot
        bot_instance_for_thread = WebSocketBot(
            ws_link,
            blocked_loggers=["DEBUG", "INFO_MSG"]
        )
        logger.info(f"[BotThread] 机器人实例初始化完毕，将连接到: {ws_link}")
        logger.info(f"[BotThread] 管理员ID配置为: {master_id}")

    except Exception as e:
        logger.error(f"[BotThread] 初始化机器人实例失败: {e}", exc_info=True)
        return

    @bot_instance_for_thread.on(GroupMessageEvent)
    async def handle_launcher_commands(event: GroupMessageEvent):
        nonlocal master_id
        if str(event.user_id) == master_id:
            if event.pure_text == "/restart":
                logger.info(f"[BotThread] 收到管理员 (UID: {event.user_id}) 的 /restart 命令")
                try:
                    await bot_instance_for_thread.send(event, "收到重启命令，正在提交，请管理员注意bot私聊重启状态", True)
                except Exception as send_exc:
                    logger.error(f"[BotThread] 发送重启确认消息失败: {send_exc}", exc_info=True)

                if loop_for_scheduler and not loop_for_scheduler.is_closed():
                    asyncio.run_coroutine_threadsafe(actual_restart_task(), loop_for_scheduler)
                    logger.info("[BotThread] 重启任务已提交到主事件循环")
                else:
                    logger.error("[BotThread] 主事件循环不可用或已关闭，无法提交重启任务")

            elif event.pure_text == "/ping":
                logger.info(f"[BotThread] 收到管理员 (UID: {event.user_id}) 的 /ping 命令")
                try:
                    await bot_instance_for_thread.send(event, "Pong! 启动器机器人线程存活", True)
                except Exception as send_exc:
                    logger.error(f"[BotThread] 发送 /ping 回复失败: {send_exc}", exc_info=True)
#
    try:
        bot_instance_for_thread.run()
    except Exception as e:
        logger.error(f"[BotThread] 机器人运行时发生严重错误: {e}", exc_info=True)
    finally:
        logger.info("[BotThread] 机器人线程执行完毕或已终止")


async def main_lifecycle_manager(shutdown_evt: asyncio.Event):
    global main_event_loop
    main_event_loop = asyncio.get_running_loop()

    logger.info("[MainLoop] 首次启动 main.py...")
    await start_main_py()

    logger.info("[MainLoop] 主生命周期管理器正在运行，等待关闭信号...")
    await shutdown_evt.wait()
    logger.info("[MainLoop] 收到关闭信号，开始清理...")
    await stop_main_py()


if __name__ == "__main__":
    try:
        if sys.stdout.encoding != 'utf-8':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
        if sys.stderr.encoding != 'utf-8':
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except (AttributeError, ValueError, io.UnsupportedOperation) as e_wrap:
        sys.__stderr__.write(f"警告：无法完全为 sys.stdout/stderr 配置UTF-8: {e_wrap}\n")

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    for handler in root_logger.handlers[:]:
        handler.close()
        root_logger.removeHandler(handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter('%(message)s'))
    try:
        if hasattr(console_handler, 'setEncoding'):
            console_handler.setEncoding('utf-8')
        else:
            sys.__stderr__.write('警告：无法为日志控制台处理器设置UTF-8编码, 函数不存在\n')
    except Exception as e_enc:
         sys.__stderr__.write(f"警告：无法为日志控制台处理器设置UTF-8编码: {e_enc}\n")
    root_logger.addHandler(console_handler)

    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    try:
        config_manager_instance = YAMLManager("run")
    except Exception as e:
        logger.error(f"启动器无法加载全局配置文件: {e}. 机器人线程将无法启动", exc_info=True)
        sys.exit(1)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    shutdown_event = asyncio.Event()

    def signal_handler(sig, frame):
        logger.info(f"{signal.Signals(sig).name} 收到，设置关闭事件")
        if not shutdown_event.is_set():
            shutdown_event.set()
            if hasattr(signal_handler, 'triggered_once'):
                logger.warning("重复收到关闭信号，将尝试更强制的退出")
            signal_handler.triggered_once = True


    try:
        loop.add_signal_handler(signal.SIGINT, signal_handler, signal.SIGINT, None)
        if sys.platform != "win32":
            loop.add_signal_handler(signal.SIGTERM, signal_handler, signal.SIGTERM, None)
    except (NotImplementedError, AttributeError, ValueError) as e_signal:
        logger.warning(f"当前平台不支持 asyncio 信号处理器 ({e_signal})，Ctrl+C 可能不会平滑关闭")
        logger.warning("请关注控制台输出以手动停止，或程序可能需要被强制终止")


    bot_t = threading.Thread(target=bot_thread_function, args=(loop, config_manager_instance), name="LauncherBotThread", daemon=True)
    bot_t.start()

    main_task = None
    try:
        logger.info("[Main] 启动主生命周期管理器...")
        main_task = loop.create_task(main_lifecycle_manager(shutdown_event))
        loop.run_until_complete(main_task)
    except KeyboardInterrupt:
        logger.info("[Main] 检测到 KeyboardInterrupt，开始关闭...")
        if not shutdown_event.is_set():
            shutdown_event.set()
        if main_task and not main_task.done():
             if not loop.is_closed():
                loop.run_until_complete(main_task)
    except Exception as e:
        logger.critical(f"[Main] 主事件循环发生未捕获的严重错误: {e}", exc_info=True)
        if not shutdown_event.is_set():
            shutdown_event.set()
        if main_task and not main_task.done() and not loop.is_closed():
            loop.run_until_complete(main_task) 
    finally:
        logger.info("[Main] 进入最终清理阶段...")
        
        if main_py_process_info["process"] and main_py_process_info["process"].returncode is None:
            logger.info("[Main] 执行最终的 main.py 停止检查 (如果尚未停止)...")
            if not loop.is_closed() and (shutdown_event.is_set() or (main_task and main_task.done() and main_task.exception() is not None)):
                try:
                    if not main_py_process_info["process"] or main_py_process_info["process"].returncode is not None:
                        logger.info("[Main] main.py 似乎已经停止")
                    else:
                        stop_task = loop.create_task(stop_main_py())
                        loop.run_until_complete(stop_task)
                except Exception as final_stop_exc:
                    logger.error(f"[Main] 在最终清理中停止 main.py 时出错: {final_stop_exc}", exc_info=True)
            elif loop.is_closed():
                logger.warning("[Main] 主循环已关闭，无法执行异步的 stop_main_py，main.py 可能仍在运行")

        logger.info("[Main] 等待机器人线程结束 (最多5秒)...")
        bot_t.join(timeout=5)
        if bot_t.is_alive():
            logger.warning("[Main] 机器人线程在超时后仍未结束")
        
        if not loop.is_closed():
            logger.info("[Main] 取消所有剩余的 asyncio 任务...")
            tasks = [t for t in asyncio.all_tasks(loop) if t is not asyncio.current_task(loop) and not t.done()]
            for task in tasks:
                task.cancel()
            
            async def _gather_remaining():
                await asyncio.sleep(0.1, loop=loop) 
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for i, result in enumerate(results):
                    if isinstance(result, asyncio.CancelledError):
                        logger.debug(f"任务 {tasks[i].get_name()} 已成功取消")
                    elif isinstance(result, Exception):
                        logger.error(f"任务 {tasks[i].get_name()} 在清理期间引发异常: {result}", exc_info=False)

            try:
                loop.run_until_complete(_gather_remaining())
            except Exception as loop_cleanup_exc:
                logger.error(f"[Main] 清理剩余 asyncio 任务时出错: {loop_cleanup_exc}", exc_info=True)
            finally:
                logger.info("[Main] 关闭主事件循环...")
                loop.close()
                logger.info("[Main] 主事件循环已关闭")
        
        asyncio.set_event_loop(None)
        logger.info("启动器已退出")
