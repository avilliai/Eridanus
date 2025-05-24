import asyncio
import os
import re
import shutil
import subprocess
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from developTools.utils.logger import get_logger

from framework_common.utils.install_and_import import install_and_import

"""
获取环境
"""
logger = get_logger()
parent_dir = os.path.dirname(os.getcwd())
# 检测上一级目录下的environments/MinGit/cmd/git.exe是否存在
custom_git_path = os.path.join(parent_dir, "environments", "MinGit", "cmd", "git.exe")
if os.path.exists(custom_git_path):
    git_path = custom_git_path
else:
    git_path = "git"
logger.info(f"git_path: {git_path}")
custom_python_path = os.path.join(parent_dir, "environments", "Python311", "python.exe")

python_path = sys.executable
logger.info(f"python_path: {python_path}")
try:
    from pip._internal.cli.main import main as pip_main
except ImportError as e:
    logger.info("Cannot import pip")
pip_main(['config', 'set', 'global.index-url', 'https://mirrors.aliyun.com/pypi/simple/'])


async def main():
    logger.info("""请输入要执行的指令：
        [1].youtube登录
        [2].更新bot代码(常用)
        [3].playwright工具安装
        [4].开发者工具
        [5].若只的检测相关ai库(如奶龙检测)
        [6].B站 or 抖音 or 小红书 登录。不登也不影响你用
        [7].退出""")
    user_input = input("请输入指令序号：")
    if user_input == "1":
        logger.info("youtube登录")
        logger.warning(
            """
            \n
            youtube登录需要手动操作，请按照以下步骤进行：
            0.等待链接出现
            1.打开链接
            2.输入input code 后面的代码
            3.继续使用你的google账号登录
            4.完成后，在这个页面按回车(等待结束后自动退出)
            """
        )
        # 获取必要参数
        from framework_common.framework_util.yamlLoader import YAMLManager

        yamlmanager = YAMLManager.get_instance()
        proxy = yamlmanager.common_config.basic_config.get("proxy").get("http_proxy")
        pyproxies = {  # pytubefix代理
            "http": proxy,
            "https": proxy
        }

        from pytubefix import YouTube
        from pytubefix.helpers import reset_cache
        reset_cache()

        yt = YouTube(url="https://www.youtube.com/watch?v=PZnXXFrjSjg", client='IOS', proxies=pyproxies, use_oauth=True,
                     allow_oauth_cache=True)
        ys = yt.streams.get_audio_only()
        # ys.download(output_path="data/voice/cache/", filename="PZnXXFrjSjg")
    elif user_input == "2":
        updaat()
    elif user_input == "3":
        logger.info("playwright工具安装(b站动态爬取需要)")
        os.system(f"\"{python_path}\" -m playwright install chromium")
    elif user_input == "4":
        logger.info("""请输入开发者工具序号：
#
        2 没想好呢""")
        user_input2 = input("请输入开发者工具序号：")
        '''if user_input2=="1":
            logger.info("同步gemini函数调用到openai函数调用")
            r = gemini_func_map()
            convert_gemini_to_openai(r)
            logger.info("同步完成")'''
    elif user_input == "5":
        logger.info("安装奶龙相关ai库依赖中")
        ai_req()
    elif user_input == "6":

        PyExecJS = install_and_import("PyExecJS")
        gi = install_and_import("PyGObject", "gi")

        from run.streaming_media.service.Link_parsing.core.login_core import login_core_select
        await login_core_select()


def updaat(f=False, source=None, yamls:dict=None):
    if not yamls:
        yamls = {}
    sources = [
        "https://github.com/avilliai/Eridanus.git",
        "https://github.akams.cn/https://github.com/avilliai/Eridanus.git",
        "https://github.moeyy.xyz/https://github.com/avilliai/Eridanus",
        "https://mirror.ghproxy.com/https://github.com/avilliai/Eridanus",
        "https://ghfast.top/https://github.com/avilliai/Eridanus.git",
        "https://gh.llkk.cc/https://github.com/avilliai/Eridanus.git"
    ]
    if source is None:
        for i in sources:
            logger.info(f"{sources.index(i)}. {i}")
        logger.info("拉取bot代码\n--------------------")
        source = input("选择更新源(输入数字 )：")

    if source.isdigit():
        source = int(source)
        if source < 0 or source > len(sources):
            logger.error("无效输入，重新执行")
            updaat()
        # os.system("git pull https://github.com/avilliai/Manyana.git")
        # 启动进程
        p = subprocess.Popen([f'{git_path}', 'pull', sources[source]], stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)

    else:
        logger.error("无效输入，重新执行")
        updaat()
    # 获取进程的输出和错误信息
    stdout, stderr = p.communicate()
    stdout = stdout.decode('utf-8', errors='ignore')
    stderr = stderr.decode('utf-8', errors='ignore')
    logger.info(stdout)
    logger.warning(stderr)

    # 标记是否在错误信息中
    in_error_info = False

    # 存放冲突文件名的列表
    conflict_files = []
    if f:
        if os.path.exists("./temp"):
            for i in yamls:
                logger.info("开始处理" + i)
                if os.path.exists(i):
                    conflict_file_dealter(yamls[i], i)
                else:
                    logger.warning("文件" + i + "于新代码中不存在，跳过")

            # shutil.rmtree("./temp")
        logger.info("处理冲突文件完成")
        logger.info("旧的冲突文件被保存到了temp文件夹，以防万一你需要它们。")
        logger.info("是否检查依赖？按任意键开始，如不需要请直接关闭此窗口。如后续启动报错，请返回此步骤并执行依赖检查。")
        logger.warning("是否检查依赖？按任意键开始，如不需要请直接关闭此窗口。如后续启动报错，请返回此步骤并执行依赖检查。")
        logger.error("是否检查依赖？按任意键开始，如不需要请直接关闭此窗口。如后续启动报错，请返回此步骤并执行依赖检查。")
        input()
        logger.warning("开始检查依赖....请不要关闭窗口")
        logger.warning("开始检查依赖....请不要关闭窗口")
        logger.warning("开始检查依赖....请不要关闭窗口")
        logger.warning("开始检查依赖....请不要关闭窗口")
        logger.warning("开始检查依赖....请不要关闭窗口")
        check_requirements("requirements.txt")
        logger.warning("依赖检查完成，开始依赖约束检查")
        logger.error("出现红色、黄色警告为正常现象，请忽略")
        logger.warning("出现红色、黄色警告为正常现象，请忽略")
        logger.error("出现红色、黄色警告为正常现象，请忽略")
        logger.warning("出现红色、黄色警告为正常现象，请忽略")
        fuck_requirements()
        logger.info("更新成功，请关闭此窗口，重新启动bot")
        input()
    # 逐行检查错误信息
    for line in stderr.split('\n'):
        # 标记冲突文件名开始位置
        if 'error: Your local changes to the following files would be overwritten by merge:' in line:
            in_error_info = True
            continue  # 结束当前循环，进入下一个循环
        elif 'error: 您对下列文件的本地修改将被合并操作覆盖：' in line:
            in_error_info = True
            continue
        # 标记冲突文件名结束位置
        if 'Please commit your changes or stash them before you merge.' in line:
            in_error_info = False
        elif '请在合并前提交或贮藏您的修改。' in line:
            in_error_info = False
        # 将冲突文件名添加到列表
        if in_error_info:
            conflict_files.append(line.strip())

    for file in conflict_files:
        print('冲突文件:', file)
        logger.warning("开始处理冲突文件")
        if file.endswith(".py"):
            os.remove(file)
            try:
                shutil.os.remove(file)
            except:
                pass
            logger.warning("移除了" + file)
        elif file.endswith(".yaml"):
            logger.info("冲突的配置文件" + file)
            logger.warning("开始处理冲突文件.....读取中")
            yamls[file] = f"temp/{file.replace('/', '_')}"
            if not os.path.exists("./temp"):
                os.mkdir("./temp")
            try:
                shutil.copyfile(file, f"temp/{file.replace('/', '_')}")
                os.remove(file)
                try:
                    shutil.os.remove(file)
                except:
                    pass
            except:
                continue

        else:
            os.remove(file)
            try:
                shutil.os.remove(file)
            except:
                pass
            logger.warning("移除了 " + file)
            # logger.warning("请自行决定删除或修改文件名称，在重新拉取后根据旧文件重新填写新文件")
    logger.warning("开始处理冲突文件")
    logger.info("即将再次执行拉取操作")
    updaat(True, str(source), yamls)

    p.wait()

    logger.info("结束")
    logger.info("如更新成功请自行查看 更新日志.yaml")


try:
    from ruamel.yaml import YAML
except Exception as e:
    logger.error("未安装ruamel.yaml库，无法处理冲突文件，开始安装缺少的依赖")
    pip_main(['install', 'ruamel.yaml'])
    from ruamel.yaml import YAML
# 创建一个YAML对象来加载和存储YAML数据
yaml = YAML()
yaml.preserve_quotes = True  # 保留引号
yaml.indent(mapping=2, sequence=4, offset=2)  # 设置缩进样式


def merge_dicts(old, new):
    for k, v in old.items():
        # 如果值是一个字典，并且键在新的yaml文件中，那么我们就递归地更新键值对
        if isinstance(v, dict) and k in new and isinstance(new[k], dict):
            merge_dicts(v, new[k])
        # 如果值是列表，且新旧值都是列表，则合并并去重
        elif isinstance(v, list) and k in new and isinstance(new[k], list):
            if k == "api_keys" or k == "sdUrl" or k == "其他默认绘图参数" or k == "card_index":  # 特殊处理, 保留旧值
                logger.info(f"覆盖列表 key: {k}")
                new[k] = v  # 使用旧的列表覆盖新的列表
            else:
                logger.info(f"合并列表 key: {k}")
                new[k] = list(dict.fromkeys(new[k] + v))  # 保持顺序去重
        # 如果键在新的yaml文件中，但值类型不同，以新值为准
        elif k in new and type(v) != type(new[k]):
            logger.info(f"类型冲突，保留新的值 key: {k}, old value type: {type(v)}, new value type: {type(new[k])}")
            continue  # 跳过对新值的覆盖
        # 如果键在新的yaml文件中且类型一致，则更新值
        elif k in new:
            logger.info(f"更新 key: {k}, old value: {v}, new value: {new[k]}")
            new[k] = v
        # 如果键不在新的yaml中，直接添加
        else:
            logger.info(f"移除键 key: {k}, value: {v}")


def conflict_file_dealter(file_old='old_aiReply.yaml', file_new='new_aiReply.yaml'):
    # 加载旧的YAML文件
    with open(file_old, 'r', encoding="utf-8") as file:
        old_data = yaml.load(file)

    # 加载新的YAML文件
    with open(file_new, 'r', encoding="utf-8") as file:
        new_data = yaml.load(file)

    # 遍历旧的YAML数据并更新新的YAML数据中的相应值
    merge_dicts(old_data, new_data)

    # 把新的YAML数据保存到新的文件中，保留注释
    with open(file_new, 'w', encoding="utf-8") as file:
        yaml.dump(new_data, file)


"""
依赖检测
"""


def fuck_requirements():
    from ruamel.yaml import YAML

    yaml = YAML(typ='safe')
    with open('data/system/requirements.yaml', 'r', encoding='utf-8') as f:
        local_config = yaml.load(f)
    update_requirements = local_config.get("update")
    for i in update_requirements:
        try:
            logger.info(f"开始更新依赖{i}...")
            pip_main(['install', '--upgrade', i])
        except Exception as e:
            logger.error(f"更新依赖{i}失败：{e}")
    for i in local_config.get("restrict"):
        try:
            logger.info(f"开始安装依赖{i}...")
            pip_main(['install', i])
        except Exception as e:
            logger.error(f"安装依赖{i}失败：{e}")


def parse_requirements(file_path):
    """
    解析 requirements.txt 文件，返回包名和版本需求信息。
    """
    requirements = {}
    requirement_pattern = re.compile(r'([a-zA-Z0-9_.-]+)([<>=!~].*)?')
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):  # 跳过空行和注释
                continue
            match = requirement_pattern.match(line)
            if match:
                pkg = match.group(1).lower()  # 包名
                spec = match.group(2)  # 版本约束
                requirements[pkg] = spec.strip() if spec else None
            else:
                print(f"无法解析行：'{line}'，请检查格式是否正确。")
    return requirements


def get_installed_packages():
    """
    使用 pip 获取已安装的包和版本信息。
    """
    result = subprocess.run(
        ['pip', 'freeze'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    installed_packages = {}
    logger.info(f"获取已安装包中...")
    logger.info(f"{result.stdout}")
    if result.returncode == 0:
        for line in result.stdout.splitlines():
            if '==' in line:
                pkg, version = line.split('==')
                installed_packages[pkg.strip()] = version.strip()
    else:
        print(f"获取已安装包失败：{result.stderr}")
    return installed_packages


def check_requirements(requirements_file):
    """
    检查 requirements.txt 中的依赖是否已安装。
    """
    if not os.path.exists(requirements_file):
        print(f"文件 {requirements_file} 不存在！")
        return

    requirements = parse_requirements(requirements_file)

    installed_packages = get_installed_packages()

    normalize_package_name = lambda name:name.lower().replace('_', '-')
    installed_packages = {normalize_package_name(k): v for k, v in installed_packages.items()}
    requirements = {normalize_package_name(k): v for k, v in requirements.items()}

    missing = []
    mismatched = []

    for pkg, required_version in requirements.items():
        if pkg not in installed_packages:
            missing.append(pkg)
        elif required_version and installed_packages[pkg] != required_version:
            mismatched.append((pkg, required_version, installed_packages[pkg]))

    if missing:
        print("缺失的包：")
        for pkg in missing:
            print(f"  - {pkg}")
            if "<" in pkg or ">" in pkg or "=" in pkg:
                pip_main(['install', pkg])
            else:
                pip_main(['install', '--upgrade', pkg])

    if mismatched:
        print("\n版本不匹配的包(一般不用管这个)：")
        for pkg, required_version, installed_version in mismatched:
            print(f"  - {pkg}: 需要 {required_version}, 已安装 {installed_version}")

    if not missing and not mismatched:
        print("所有依赖都已正确安装！")


def extract_cuda_version(nvcc_output):
    """
    从nvcc --version命令的输出中提取CUDA版本，并转换为用于构建PyTorch URL的形式。
    :param nvcc_output: str, nvcc --version命令的输出字符串。
    :return: str, 转换后的CUDA版本号，如'cu121'。
    """
    match = re.search(r'release (\d+\.\d+)', nvcc_output)
    if match:
        cuda_version = match.group(1)  # 获取主版本和次版本号
        major, minor = cuda_version.split('.')
        return f'cu{major}{minor}'
    else:
        return None


def ai_req():
    try:
        nvcc_output = subprocess.check_output(["nvcc", "--version"], stderr=subprocess.STDOUT).decode()
        cuda_torch_suffix = extract_cuda_version(nvcc_output)
        if cuda_torch_suffix:
            logger.info(f"检测到CUDA版本：{cuda_torch_suffix[2:]}，正在安装支持CUDA的PyTorch...")
        else:
            logger.warning("未能检测到CUDA版本，假设系统中未安装CUDA。")
    except Exception:
        logger.exception('CUDA')
        logger.warning("未能检测到CUDA版本或nvcc未安装，假设系统中未安装CUDA。")
        cuda_torch_suffix = None

    try:
        pip_main(['install', 'opencv-python-headless'])
        if cuda_torch_suffix:
            # 如果检测到了支持的CUDA版本，则安装带有CUDA支持的PyTorch包
            pip_main(['install', 'torch', 'torchvision', 'torchaudio',
                      f'--index-url=https://download.pytorch.org/whl/{cuda_torch_suffix}'])
        else:
            # 如果没有检测到CUDA或不支持的CUDA版本，则安装CPU-only版本的PyTorch包
            logger.info("未检测到CUDA或CUDA版本不受支持，正在安装仅CPU版本的PyTorch...")
            pip_main(['install', 'opencv-python-headless', 'torch', 'torchvision', 'torchaudio'])
    except subprocess.CalledProcessError as e:
        logger.error(f"安装PyTorch时出错：{e}")
        sys.exit(1)

    logger.info("ai相关库安装成功完成")
    return

if __name__ == '__main__':
    asyncio.run(main())
