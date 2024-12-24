import os
from ruamel.yaml import YAML
from typing import Any

class YAMLManager:
    def __init__(self, yaml_files: list):
        """
        初始化 YAML 管理器。

        :param yaml_files: YAML 文件路径列表
        """
        self.yaml = YAML()
        self.yaml.preserve_quotes = True  # 保留引号
        self.data = {}  # 存储所有加载的 YAML 数据
        self.file_paths = {}  # 文件名到路径的映射

        for file_path in yaml_files:
            file_name = os.path.basename(file_path).split('.')[0]  # 获取文件名（无扩展名）
            self.file_paths[file_name] = file_path
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    self.data[file_name] = self.yaml.load(file)
            else:
                raise FileNotFoundError(f"YAML file {file_path} not found.")

    def save_yaml(self, file_name: str):
        """
        保存某个 YAML 数据到文件。

        :param file_name: YAML 文件名（无扩展名）
        """
        if file_name not in self.file_paths:
            raise ValueError(f"YAML file {file_name} not managed by YAMLManager.")

        file_path = self.file_paths[file_name]
        with open(file_path, 'w', encoding='utf-8') as file:
            self.yaml.dump(self.data[file_name], file)

    def __getattr__(self, name: str):
        """
        允许通过属性访问 YAML 数据。

        :param name: YAML 文件名（无扩展名）
        :return: YAML 数据
        """
        if name in self.data:
            return self.data[name]
        raise AttributeError(f"YAMLManager has no attribute '{name}'.")

    def __setattr__(self, name: str, value: Any):
        """
        允许通过属性修改 YAML 数据。

        :param name: YAML 文件名（无扩展名）
        :param value: 新的 YAML 数据
        """
        if name in ["yaml", "data", "file_paths"]:
            super().__setattr__(name, value)
        elif name in self.data:
            self.data[name] = value
            self.save_yaml(name)
        else:
            raise AttributeError(f"YAMLManager has no attribute '{name}'.")

# 使用示例
if __name__ == "__main__":
    manager = YAMLManager(["config/api.yaml", "config/controller.yaml"])

    # 访问 YAML 数据
    print(manager.api["llm"]["apikey"])

    # 修改 YAML 数据onfig["llm"]["apikey"] = "new-api-key"
    #     manager.save
    manager.llmC_yaml("api")

    # 再次访问以确认修改
    print(manager.api["llm"]["apikey"])