
from ruamel.yaml import YAML
from yiriob.adapters.base import Adapter
from yiriob.bot import Bot
class ExtendedBot(Bot):
    def __init__(self, adapter: Adapter, self_id: int, config_files: dict[str, str]) -> None:
        super().__init__(adapter, self_id)
        for key, filepath in config_files.items():
            setattr(self, key, self.load_yaml(filepath))

    def load_yaml(self, yaml_path: str):
        """从 YAML 文件加载数据并返回为字典。"""
        with open(yaml_path, 'r', encoding='utf-8') as f:
            yaml_loader = YAML()
            data = yaml_loader.load(f)
        return data

