import importlib.util

from pip._internal.cli.main import main as pip_main
from developTools.utils.logger import get_logger

logger=get_logger()
"""
CWS Ps:os.system很好 以后别用了。。。
这就是我的替身install and import，装和导
(以防有人没看懂，这里是捏他soft and wet，那么问题来了，soft and wet是什么？)
"""
def install_and_import(package_name, import_name=None):
    """检测模块是否已安装，若未安装则通过 pip 安装"""
    if import_name is None:
        import_name = package_name

    spec = importlib.util.find_spec(import_name)
    if spec is None:
        logger.warning(f"{package_name} 未安装，正在安装...")
        pip_main(['install', package_name])
        spec = importlib.util.find_spec(import_name)
        if spec is None:
            logger.error(f"安装失败：无法找到 {import_name} 模块")
            return None

    return importlib.import_module(import_name)