import asyncio
import os
import shutil
import subprocess
from time import sleep

from ruamel.yaml import YAML

from developTools.utils.logger import get_logger
from plugins.utils.convert_func_calling import gemini_func_map, convert_gemini_to_openai
"""
获取环境
"""
logger=get_logger()
parent_dir = os.path.dirname(os.getcwd())
# 检测上一级目录下的environments/MinGit/cmd/git.exe是否存在
custom_git_path = os.path.join(parent_dir, "environments", "MinGit", "cmd", "git.exe")
if os.path.exists(custom_git_path):
    git_path = custom_git_path
else:
    git_path = "git"
logger.info(f"git_path: {git_path}")
custom_python_path = os.path.join(parent_dir, "environments", "Python311", "python.exe")
if os.path.exists(custom_python_path):
    python_path = custom_python_path
elif os.path.exists("./venv/Scripts/python.exe"):
    python_path = "./venv/Scripts/python.exe"
else:
    python_path = "python"
logger.info(f"python_path: {python_path}")
custom_pip_path = os.path.join(parent_dir, "environments", "Python311", "Scripts", "pip.exe")
if os.path.exists(custom_pip_path):
    pip_path = custom_pip_path
elif os.path.exists("./venv/Scripts/pip.exe"):
    pip_path = "./venv/Scripts/pip.exe"
else:
    pip_path = "pip"
logger.info(f"pip_path: {pip_path}")

async def main():
    logger.info("""请输入要执行的指令：
        1 youtube登录
        2 更新bot代码
        3 开发者工具""")
    sleep(1)
    user_input=input("请输入指令序号：")
    print(user_input)
    if user_input=="1":
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
        #获取必要参数
        yaml = YAML(typ='safe')
        with open('config/api.yaml', 'r', encoding='utf-8') as f:
            local_config = yaml.load(f)
        proxy = local_config.get("proxy").get("http_proxy")
        pyproxies = {  # pytubefix代理
            "http": proxy,
            "https": proxy
        }

        from pytubefix import YouTube
        from pytubefix.helpers import reset_cache
        reset_cache()

        yt = YouTube(url="https://www.youtube.com/watch?v=PZnXXFrjSjg", client='IOS', proxies=pyproxies, use_oauth=True, allow_oauth_cache=True)
        ys = yt.streams.get_audio_only()
        #ys.download(output_path="data/voice/cache/", filename="PZnXXFrjSjg")
    elif user_input=="2":
        updaat()
    elif user_input=="3":
        logger.info("""请输入开发者工具序号：
        1 同步gemini函数调用到openai函数调用
        2 没想好呢""")
        sleep(1)
        user_input2=input("请输入开发者工具序号：")
        if user_input2=="1":
            logger.info("同步gemini函数调用到openai函数调用")
            r = gemini_func_map()
            convert_gemini_to_openai(r)
            logger.info("同步完成")

def updaat(f=False,jump=False,source=None,yamls={}):
    if jump==False:
        logger.warning("是否补全依赖？如已使用最新整合包请输入1以跳过。(更新的新功能可能需要执行此步骤)。可以按1跳过，如果更新后启动报错/提示功能无法启用，请回来执行这一步")
        if input("在这里输入:") != "1":
            logger.warning("即将开始更新依赖库，请确保已关闭代理，否则无法安装依赖库")
            input("按任意键继续：")
            os.system(f"\"{python_path}\" -m pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/")
            #print(str(custom_pip_path)+"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!5555555!!!!!!!!!!!!!!!")
            os.system(f"\"{python_path}\" -m pip install --upgrade jmcomic")
            os.system(f"\"{python_path}\" -m pip install img2pdf")
            os.system(f"\"{python_path}\" -m pip install --upgrade lanzou-api")
            os.system(f"\"{python_path}\" -m pip install --upgrade pytubefix")
            os.system(f"\"{python_path}\" -m pip install --upgrade PicImageSearch")
            os.system(f"\"{python_path}\" -m pip install httpx==0.27.2")
    if source==None:
        logger.info("拉取bot代码\n--------------------")
        logger.info("选择更新源(git源 镜像源相互兼容)：\n1 git源\n2 git代理源1\n3 git代理源2")
        source = input("选择更新源(输入数字 )：")
    else:
        source=str(source)
    if source == "1":
        # os.system("git pull https://github.com/avilliai/Manyana.git")
        # 启动进程
        p = subprocess.Popen([f'{git_path}', 'pull', 'https://github.com/avilliai/Eridanus.git'], stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    elif source=="2":
        p = subprocess.Popen([f'{git_path}', 'pull', 'https://github.moeyy.xyz/https://github.com/avilliai/Eridanus'], stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    elif source=="3":
        p=subprocess.Popen([f'{git_path}', 'pull', 'https://mirror.ghproxy.com/https://github.com/avilliai/Eridanus'], stdout=subprocess.PIPE,stderr=subprocess.PIPE)

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
    if f==True:
        if os.path.exists("./temp"):
            for i in yamls:
                logger.info("开始处理"+i)
                if os.path.exists(i):
                    conflict_file_dealter(i,yamls[i])
                else:
                    logger.warning("文件"+i+"于新代码中不存在，跳过")

            #shutil.rmtree("./temp")
        logger.info("处理冲突文件完成")
        logger.info("旧的冲突文件被保存到了temp文件夹，以防万一你需要它们。")
        logger.info("你可以关闭此窗口了")
        input()
    # 逐行检查错误信息
    for line in stderr.split('\n'):
        # 标记冲突文件名开始位置
        if 'error: Your local changes to the following files would be overwritten by merge:' in line:
            in_error_info = True
            continue  # 结束当前循环，进入下一个循环
        elif 'error: 您对下列文件的本地修改将被合并操作覆盖：' in line:
            in_error_info=True
            continue
        # 标记冲突文件名结束位置
        if 'Please commit your changes or stash them before you merge.' in line:
            in_error_info = False
        elif '请在合并前提交或贮藏您的修改。' in line:
            in_error_info=False
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
            yamls[file]=f"temp/{file.replace('/','_')}"
            if not os.path.exists("./temp"):
                os.mkdir("./temp")
            try:
                shutil.copyfile(file, f"temp/{file.replace('/','_')}")
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
            #logger.warning("请自行决定删除或修改文件名称，在重新拉取后根据旧文件重新填写新文件")
    logger.warning("开始处理冲突文件")
    logger.info("即将再次执行拉取操作")
    updaat(True,True,str(source),yamls)

    p.wait()


    logger.info("结束")
    logger.info("如更新成功请自行查看 更新日志.yaml")

try:
    from ruamel.yaml import YAML
except Exception as e:
    logger.error("未安装ruamel.yaml库，无法处理冲突文件，开始安装缺少的依赖")
    os.system(f"\"{python_path}\" -m pip install ruamel.yaml")
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
            logger.info(f"添加新键 key: {k}, value: {v}")
            new[k] = v

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

asyncio.run(main())
