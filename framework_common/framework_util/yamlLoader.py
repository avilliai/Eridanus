import os
from ruamel.yaml import YAML
from typing import Any

class YAMLManager:
    _instance = None

    def __init__(self,plugins_dir=None):
        """
        初始化 YAML 管理器，自动加载 run 目录下及各插件文件夹中的 YAML 文件。
        """
        self.yaml = YAML()
        self.yaml.preserve_quotes = True  # 保留引号
        self.data = {}  # 存储所有加载的 YAML 数据，结构为 {plugin_name: {config_name: data}} 或 {config_name: data}（对于 run 目录下的文件）
        self.file_paths = {}  # 配置文件名到路径的映射，结构为 {plugin_name: {config_name: path}} 或 {config_name: path}（对于 run 目录下的文件）

        # 加载 run 目录下的 YAML 文件
        run_dir = os.path.join(os.getcwd(), plugins_dir or "run")
        if not os.path.exists(run_dir):
            raise FileNotFoundError(f"Run directory {run_dir} not found.")

        # 直接加载 run 目录下的 YAML 文件
        for file_name in os.listdir(run_dir):
            if file_name.endswith(".yaml") or file_name.endswith(".yml"):
                file_path = os.path.join(run_dir, file_name)
                config_name = os.path.splitext(file_name)[0]
                self.file_paths[config_name] = file_path
                with open(file_path, 'r', encoding='utf-8') as file:
                    self.data[config_name] = self.yaml.load(file)

        # 加载插件文件夹中的 YAML 文件
        for plugin_folder in os.listdir(run_dir):
            plugin_path = os.path.join(run_dir, plugin_folder)
            if os.path.isdir(plugin_path):
                self.data[plugin_folder] = {}
                self.file_paths[plugin_folder] = {}
                for file_name in os.listdir(plugin_path):
                    if file_name.endswith(".yaml") or file_name.endswith(".yml"):
                        file_path = os.path.join(plugin_path, file_name)
                        config_name = os.path.splitext(file_name)[0]
                        self.file_paths[plugin_folder][config_name] = file_path
                        with open(file_path, 'r', encoding='utf-8') as file:
                            self.data[plugin_folder][config_name] = self.yaml.load(file)

        YAMLManager._instance = self

    @staticmethod
    def get_instance() -> 'YAMLManager':
        """
        获取已创建的 YAMLManager 实例。

        :return: YAMLManager 实例
        """
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
                class PluginConfig:
                    def __init__(self, data, file_paths, save_func):
                        self._data = data
                        self._file_paths = file_paths
                        self._save_func = save_func

                    def __getattr__(self, config_name):
                        if config_name in self._data:
                            return self._data[config_name]
                        raise AttributeError(f"Plugin {name} has no config '{config_name}'.")

                    def __setattr__(self, config_name, value):
                        if config_name in ["_data", "_file_paths", "_save_func"]:
                            super().__setattr__(config_name, value)
                        elif config_name in self._data:
                            self._data[config_name] = value
                            self._save_func(config_name, name)
                        else:
                            raise AttributeError(f"Plugin {name} has no config '{config_name}'.")

                return PluginConfig(self.data[name], self.file_paths[name], self.save_yaml)
            else:  # 直接在 run 目录下的 YAML 文件
                return self.data[name]
        raise AttributeError(f"YAMLManager has no plugin or config '{name}'.")

    def __setattr__(self, name: str, value: Any):
        """
        允许通过属性修改 YAML 数据。

        :param name: 属性名（插件名或配置文件名）
        :param value: 新值
        """
        if name in ["yaml", "data", "file_paths", "_instance"]:
            super().__setattr__(name, value)
        elif name in self.data and not isinstance(self.data[name], dict):  # 直接在 run 目录下的 YAML 文件
            self.data[name] = value
            self.save_yaml(name)
        else:
            raise AttributeError(f"YAMLManager cannot set attribute '{name}' directly. Use plugin.config notation for plugins or config for root files.")

# 使用示例
if __name__ == "__main__":
    # 获取 YAMLManager 实例
    manager = YAMLManager.get_instance()

    # 假设 run/api.yaml 存在（直接在 run 目录下）
    print(manager.api["llm"]["apikey"])

    # 修改 run/api.yaml 的数据
    manager.api["llm"]["apikey"] = "new-api-key"

    # 假设 run/plugin1/config.yaml 存在
    print(manager.plugin1.config["setting"]["value"])

    # 修改 run/plugin1/config.yaml 的数据
    manager.plugin1.config["setting"]["value"] = "new-value"