import os
from ruamel.yaml import YAML
from typing import Any
from concurrent.futures import ThreadPoolExecutor
import threading


class PluginConfig:
    def __init__(self, name, data, file_paths, save_func):
        self._data = data
        self._file_paths = file_paths
        self._name = name
        self._save_func = save_func
        dir(self)

    def __getattr__(self, config_name):
        if config_name in ["_data", "_file_paths", "_save_func", "_name"]:
            return self.__getattribute__(config_name)
        if config_name in self._data:
            return self._data[config_name]
        raise AttributeError(f"Plugin {self._name} has no config '{config_name}'.")

    def __setattr__(self, config_name, value):
        if config_name in ["_data", "_file_paths", "_save_func", "_name"]:
            super().__setattr__(config_name, value)
        elif config_name in self._data:
            self._data[config_name] = value
            self._save_func(config_name, self._name)
        else:
            raise AttributeError(f"Plugin {self._name} has no config '{config_name}'.")

class YAMLManager:
    _instance = None
    _lock = threading.Lock()  # 线程安全的单例初始化

    def __init__(self, plugins_dir=None):
        """
        初始化 YAML 管理器，自动并行加载 run 目录下及各插件文件夹中的 YAML 文件。
        """
        self.yaml = YAML()
        self.data = {}  # 存储所有加载的 YAML 数据
        self.file_paths = {}  # 配置文件名到路径的映射

        # 加载 run 目录下的 YAML 文件
        run_dir = os.path.join(os.getcwd(), plugins_dir or "run")
        if not os.path.exists(run_dir):
            raise FileNotFoundError(f"Run directory {run_dir} not found.")

        # 收集所有需要加载的 YAML 文件
        yaml_files = []

        # 插件文件夹中的 YAML 文件
        for plugin_folder in os.listdir(run_dir):
            plugin_path = os.path.join(run_dir, plugin_folder)
            if os.path.isdir(plugin_path):
                for file_name in os.listdir(plugin_path):
                    if file_name.endswith((".yaml", ".yml")):
                        file_path = os.path.join(plugin_path, file_name)
                        config_name = os.path.splitext(file_name)[0]
                        yaml_files.append((plugin_folder, config_name, file_path))
            elif os.path.isfile(plugin_path):
                if plugin_folder.endswith((".yaml", ".yml")):
                    file_path = os.path.join(run_dir, plugin_folder)
                    config_name = os.path.splitext(plugin_folder)[0]
                    yaml_files.append((None, config_name, file_path))

        # 并行加载 YAML 文件
        def load_yaml_file(args):
            plugin_name, config_name, file_path = args
            yaml_instance = YAML()  # 为每个线程创建独立的 YAML 实例
            yaml_instance.preserve_quotes = True
            yaml_instance.allow_duplicate_keys = True
            with open(file_path, 'r', encoding='utf-8') as file:
                return plugin_name, config_name, file_path, yaml_instance.load(file)

        with ThreadPoolExecutor() as executor:
            for plugin_name, config_name, file_path, data in executor.map(load_yaml_file, yaml_files):
                if plugin_name is None:
                    self.data[config_name] = data
                    self.file_paths[config_name] = file_path
                else:
                    if plugin_name not in self.data:
                        self.data[plugin_name] = {}
                        self.file_paths[plugin_name] = {}
                    self.data[plugin_name][config_name] = data
                    self.file_paths[plugin_name][config_name] = file_path


        YAMLManager._instance = self

    @staticmethod
    def get_instance() -> 'YAMLManager':
        """
        获取已创建的 YAMLManager 实例（线程安全）。

        :return: YAMLManager 实例
        """
        with YAMLManager._lock:
            if YAMLManager._instance is None:
                YAMLManager._instance = YAMLManager()
            return YAMLManager._instance

    def save_yaml(self, config_name: str, plugin_name: str = None):
        """
        保存某个 YAML 数据到文件。

        :param config_name: YAML 配置文件名（无扩展名）
        :param plugin_name: 插件名称（对于 run 目录下的文件，此参数为 None）
        """
        if plugin_name is None:
            if config_name not in self.file_paths:
                raise ValueError(f"YAML file {config_name} not managed by YAMLManager.")
            file_path = self.file_paths[config_name]
            data = self.data[config_name]
        else:
            if plugin_name not in self.file_paths or config_name not in self.file_paths[plugin_name]:
                raise ValueError(f"YAML file {config_name} in plugin {plugin_name} not managed by YAMLManager.")
            file_path = self.file_paths[plugin_name][config_name]
            data = self.data[plugin_name][config_name]

        with open(file_path, 'w', encoding='utf-8') as file:
            self.yaml.dump(data, file)

    def __getattr__(self, name: str):
        """
        允许通过属性访问插件或直接 YAML 数据。

        :param name: 插件名称或 YAML 配置文件名（无扩展名）
        :return: 插件的配置数据字典或直接的 YAML 数据
        """
        if name in self.data:
            if isinstance(self.data[name], dict):  # 插件文件夹
                return PluginConfig(name, self.data[name], self.file_paths[name], self.save_yaml)
            else:  # 直接在 run 目录下的 YAML 文件
                return self.data[name]
        raise AttributeError(f"YAMLManager has no plugin or config '{name}'.")

    def __setattr__(self, name: str, value: Any):
        """
        允许通过属性修改 YAML 数据。

        :param name: 属性名（插件名或配置文件名）
        :param value: 新值
        """
        if name in ["yaml", "data", "file_paths", "_instance", "_lock"]:
            super().__setattr__(name, value)
        elif name in self.data and not isinstance(self.data[name], dict):  # 直接在 run 目录下的 YAML 文件
            self.data[name] = value
            self.save_yaml(name)
        else:
            raise AttributeError(
                f"YAMLManager cannot set attribute '{name}' directly. Use plugin.config notation for plugins or config for root files.")


# 使用示例
if __name__ == "__main__":
    # 获取 YAMLManager 实例
    manager = YAMLManager.get_instance()

    print(manager.api["llm"]["apikey"])

    manager.api["llm"]["apikey"] = "new-api-key"

    print(manager.plugin1.config["setting"]["value"])

    manager.plugin1.config["setting"]["value"] = "new-value"