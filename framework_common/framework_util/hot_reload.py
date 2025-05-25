import asyncio
import importlib
import os
import sys
import traceback
from pathlib import Path
from typing import Dict, List, Set, Optional, Callable, Tuple, Any, Type
from watchdog.observers import Observer
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent
import threading
import time

from developTools.event.eventBus import event_bus


class HotReloadManager:
    """
    热重载管理器
    负责监控插件文件变化并自动重载
    """
    
    def __init__(self, plugin_dir: str = "run", exclude_dirs: Optional[Set[str]] = None):
        self.plugin_dir = Path(plugin_dir)
        self.exclude_dirs = exclude_dirs or {"__pycache__", ".git", ".vscode"}
        
        # 存储模块引用
        self.loaded_modules: Dict[str, object] = {}
        # 存储事件监听器（全局EventBus）
        self.event_listeners: Dict[str, List[Tuple[str, Callable]]] = {}
        # 存储bot实例的事件监听器
        self.bot_event_listeners: Dict[str, Dict[Type, Set[Callable]]] = {}
        # 存储文件到模块的映射
        self.file_to_module: Dict[str, str] = {}
        
        # 存储bot实例引用
        self.bot_instances: List[object] = []
        
        # 文件监控器
        self.observer = None
        self.event_handler = PluginFileHandler(self)
        
        # 重载锁，防止并发重载
        self.reload_lock = asyncio.Lock()
        
        # 重载任务队列
        self.reload_queue: asyncio.Queue = asyncio.Queue()
        self.reload_task: Optional[asyncio.Task] = None
        
        self.logger = None  # 稍后由main设置
        
    def set_logger(self, logger):
        """设置日志记录器"""
        self.logger = logger
        
    def register_bot(self, bot):
        """注册bot实例以管理其事件监听器"""
        if bot not in self.bot_instances:
            self.bot_instances.append(bot)
            if self.logger:
                self.logger.info(f"Registered bot instance for hot reload management")
                
    def unregister_bot(self, bot):
        """注销bot实例"""
        if bot in self.bot_instances:
            self.bot_instances.remove(bot)
            if self.logger:
                self.logger.info(f"Unregistered bot instance from hot reload management")
        
    def start_monitoring(self):
        """开始监控文件变化"""
        if self.observer is not None:
            return
            
        self.observer = Observer()
        if self.observer:
            self.observer.schedule(
                self.event_handler, 
                str(self.plugin_dir), 
                recursive=True
            )
            self.observer.start()
        
        # 尝试启动重载处理任务，如果没有事件循环则延迟启动
        try:
            loop = asyncio.get_running_loop()
            self.reload_task = asyncio.create_task(self._reload_processor())
        except RuntimeError:
            # 没有运行中的事件循环，稍后启动
            if self.logger:
                self.logger.info("No running event loop, will start reload processor later")
            self.reload_task = None
        
        if self.logger:
            self.logger.info(f"Hot reload monitoring started for {self.plugin_dir}")
            
    def ensure_reload_processor(self):
        """确保重载处理器正在运行（在事件循环可用时调用）"""
        if self.reload_task is None:
            try:
                loop = asyncio.get_running_loop()
                self.reload_task = asyncio.create_task(self._reload_processor())
                if self.logger:
                    self.logger.info("Hot reload processor started")
            except RuntimeError:
                if self.logger:
                    self.logger.warning("Still no running event loop available")
            
    def stop_monitoring(self):
        """停止监控文件变化"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            
        if self.reload_task:
            self.reload_task.cancel()
            self.reload_task = None
            
        if self.logger:
            self.logger.info("Hot reload monitoring stopped")
            
    async def _reload_processor(self):
        """处理重载队列"""
        while True:
            try:
                file_path = await self.reload_queue.get()
                await self._process_file_change(file_path)
                self.reload_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Error in reload processor: {e}")
                    self.logger.error(traceback.format_exc())
                    
    async def queue_reload(self, file_path: str):
        """将文件重载请求加入队列"""
        # 确保重载处理器正在运行
        self.ensure_reload_processor()
        
        if self.reload_task is not None:
            await self.reload_queue.put(file_path)
        else:
            # 如果重载处理器还没启动，直接处理
            await self._process_file_change(file_path)
        
    async def _process_file_change(self, file_path: str):
        """处理文件变化"""
        async with self.reload_lock:
            try:
                # 延迟一下，等待文件写入完成
                await asyncio.sleep(0.5)
                
                module_name = self._get_module_name(file_path)
                if not module_name:
                    return
                    
                if self.logger:
                    self.logger.info(f"Reloading module: {module_name}")
                    
                await self._reload_module(module_name, file_path)
                
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Failed to reload {file_path}: {e}")
                    self.logger.error(traceback.format_exc())
                    
    def _get_module_name(self, file_path: str) -> Optional[str]:
        """根据文件路径获取模块名"""
        try:
            # 转换为相对路径
            rel_path = os.path.relpath(file_path, ".")
            
            # 跳过非Python文件
            if not rel_path.endswith('.py'):
                return None
                
            # 跳过__init__.py文件
            if rel_path.endswith('__init__.py'):
                return None
                
            # 跳过不在插件目录下的文件
            if not rel_path.startswith(str(self.plugin_dir)):
                return None
                
            # 转换为模块名
            module_name = rel_path.replace('/', '.').replace('\\', '.')[:-3]
            return module_name
            
        except Exception:
            return None
            
    async def _reload_module(self, module_name: str, file_path: str):
        """重载指定模块"""
        try:
            # 如果模块已经加载，先卸载事件监听器
            if module_name in self.loaded_modules:
                await self._unregister_module_events(module_name)
                
            # 重载模块
            if module_name in sys.modules:
                # 重新载入现有模块
                module = importlib.reload(sys.modules[module_name])
            else:
                # 导入新模块
                module = importlib.import_module(module_name)
                
            # 存储模块引用
            self.loaded_modules[module_name] = module
            self.file_to_module[file_path] = module_name
            
            # 重新注册事件监听器（通过执行模块的main函数）
            await self._register_module_events(module, module_name)
            
            if self.logger:
                self.logger.info(f"Successfully reloaded module: {module_name}")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to reload module {module_name}: {e}")
                self.logger.error(traceback.format_exc())
                
    async def _register_module_events(self, module, module_name: str):
        """重新注册模块的事件监听器，通过重新执行模块的main函数"""
        try:
            # 先备份当前bot实例的事件监听器状态
            for bot in self.bot_instances:
                self._backup_bot_handlers(bot, module_name)
            
            # 检查模块是否有main函数
            if hasattr(module, 'main'):
                # 为每个bot实例重新执行main函数
                for bot in self.bot_instances:
                    try:
                        # 获取main函数的参数数量
                        import inspect
                        sig = inspect.signature(module.main)
                        params = list(sig.parameters.keys())
                        
                        # 根据参数数量调用main函数
                        if len(params) == 1:
                            # main(bot)
                            module.main(bot)
                        elif len(params) == 2:
                            # main(bot, config)
                            try:
                                # 尝试获取bot的config属性
                                bot_config = getattr(bot, 'config', None)
                                module.main(bot, bot_config)
                            except:
                                module.main(bot, None)
                        else:
                            # 其他情况，尝试只传bot
                            module.main(bot)
                            
                        if self.logger:
                            self.logger.debug(f"Re-executed main function for module: {module_name}")
                            
                    except Exception as e:
                        if self.logger:
                            self.logger.error(f"Failed to re-execute main for {module_name}: {e}")
            
            # 查找并注册使用@event_handler装饰器的事件处理函数（用于全局EventBus）
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                
                # 检查是否有事件注册装饰器标记
                if hasattr(attr, '_event_handlers'):
                    for event_type, handler in attr._event_handlers:
                        # 使用事件类型的名称作为事件标识
                        event_name = event_type.__name__ if hasattr(event_type, '__name__') else str(event_type)
                        event_bus.subscribe(event_name, handler)
                        
                        # 记录监听器
                        if module_name not in self.event_listeners:
                            self.event_listeners[module_name] = []
                        self.event_listeners[module_name].append((event_name, handler))
                        
                        if self.logger:
                            self.logger.debug(f"Registered event handler: {module_name}.{attr_name} -> {event_name}")
                            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to register events for {module_name}: {e}")
                
    def _backup_bot_handlers(self, bot, module_name: str):
        """备份bot实例当前的事件监听器"""
        try:
            # 使用getattr安全访问属性
            event_bus = getattr(bot, 'event_bus', None)
            if event_bus and hasattr(event_bus, 'handlers'):
                # 备份当前的handlers状态
                current_handlers = {}
                for event_type, handlers_set in event_bus.handlers.items():
                    current_handlers[event_type] = handlers_set.copy()
                
                # 存储到bot_event_listeners中
                if module_name not in self.bot_event_listeners:
                    self.bot_event_listeners[module_name] = {}
                self.bot_event_listeners[module_name] = current_handlers
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to backup bot handlers for {module_name}: {e}")
                
    async def _unregister_module_events(self, module_name: str):
        """注销模块的事件监听器"""
        try:
            # 注销全局EventBus的事件监听器
            if module_name in self.event_listeners:
                for event_name, handler in self.event_listeners[module_name]:
                    event_bus.unsubscribe(event_name, handler)
                    
                    if self.logger:
                        self.logger.debug(f"Unregistered global event handler: {module_name} -> {event_name}")
                        
                del self.event_listeners[module_name]
            
            # 清理bot实例的事件监听器
            await self._cleanup_bot_handlers(module_name)
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to unregister events for {module_name}: {e}")
                
    async def _cleanup_bot_handlers(self, module_name: str):
        """清理bot实例中属于指定模块的事件监听器"""
        try:
            for bot in self.bot_instances:
                # 使用getattr安全访问属性
                event_bus = getattr(bot, 'event_bus', None)
                if event_bus and hasattr(event_bus, 'handlers'):
                    # 清理所有事件类型的监听器
                    # 这是一个粗暴但有效的方法：清理所有监听器，让模块重新注册
                    original_handlers = event_bus.handlers.copy()
                    event_bus.handlers.clear()
                    
                    if self.logger:
                        self.logger.debug(f"Cleared all bot event handlers for reload of {module_name}")
                        
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to cleanup bot handlers for {module_name}: {e}")
                
    async def reload_plugin(self, plugin_name: str) -> bool:
        """手动重载指定插件"""
        try:
            # 查找插件文件
            plugin_path = None
            for root, dirs, files in os.walk(self.plugin_dir):
                # 排除指定目录
                dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
                
                for file in files:
                    if file.endswith('.py') and plugin_name in file:
                        plugin_path = os.path.join(root, file)
                        break
                        
                if plugin_path:
                    break

            
            if not plugin_path:
                if self.logger:
                    self.logger.warning(f"Plugin file not found: {plugin_name}")
                return False
                
            await self._process_file_change(plugin_path)
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to reload plugin {plugin_name}: {e}")
            return False
            
    def get_loaded_modules(self) -> List[str]:
        """获取已加载的模块列表"""
        return list(self.loaded_modules.keys())


class PluginFileHandler(FileSystemEventHandler):
    """文件系统事件处理器"""
    
    def __init__(self, reload_manager: HotReloadManager):
        self.reload_manager = reload_manager
        self.last_modified = {}
        
    def on_modified(self, event):
        if isinstance(event, FileModifiedEvent) and str(event.src_path).endswith('.py'):
            self._handle_file_change(str(event.src_path))
            
    def on_created(self, event):
        if isinstance(event, FileCreatedEvent) and str(event.src_path).endswith('.py'):
            self._handle_file_change(str(event.src_path))
            
    def _handle_file_change(self, file_path: str):
        """处理文件变化事件"""
        try:
            # 防止重复触发
            current_time = time.time()
            if file_path in self.last_modified:
                if current_time - self.last_modified[file_path] < 1.0:  # 1秒内的重复事件忽略
                    return
                    
            self.last_modified[file_path] = current_time
            
            # 尝试异步处理重载
            try:
                loop = asyncio.get_running_loop()
                asyncio.create_task(self.reload_manager.queue_reload(file_path))
            except RuntimeError:
                # 没有事件循环，使用线程处理
                threading.Thread(
                    target=self._sync_reload_handler, 
                    args=(file_path,), 
                    daemon=True
                ).start()
            
        except Exception as e:
            if self.reload_manager.logger:
                self.reload_manager.logger.error(f"Error handling file change {file_path}: {e}")
                
    def _sync_reload_handler(self, file_path: str):
        """在没有事件循环时的同步重载处理"""
        try:
            # 创建新的事件循环来处理重载
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.reload_manager._process_file_change(file_path))
            finally:
                loop.close()
        except Exception as e:
            if self.reload_manager.logger:
                self.reload_manager.logger.error(f"Error in sync reload handler: {e}")


# 全局热重载管理器实例
hot_reload_manager = HotReloadManager()


def event_handler(*event_types):
    """
    事件处理器装饰器
    支持热重载的事件注册
    """
    def decorator(func):
        # 标记函数为事件处理器
        if not hasattr(func, '_event_handlers'):
            func._event_handlers = []
            
        for event_type in event_types:
            func._event_handlers.append((event_type, func))
            
        return func
    return decorator
