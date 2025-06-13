# encoding: utf-8
import asyncio
import functools
import importlib
import json
import logging
import os
import shutil
import sys
import time
from io import StringIO

from cryptography.fernet import Fernet
from flask import Flask, request, jsonify, make_response, send_file, send_from_directory
from flask_cors import CORS
from ruamel.yaml import YAML, comments
from ruamel.yaml.scalarint import ScalarInt
from ruamel.yaml.scalarstring import DoubleQuotedScalarString, SingleQuotedScalarString

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from developTools.utils.logger import get_logger
from framework_common.utils.install_and_import import install_and_import
from userdb_query import get_users_range, get_users_count, search_users_by_id, get_user_signed_days

flask_sock = install_and_import("flask_sock")
from flask_sock import Sock

psutil = install_and_import("psutil")
httpx = install_and_import("httpx")

# 全局变量，用于存储 logger 实例和屏蔽的日志类别
_logger = None
_blocked_loggers = []

app = Flask(__name__, static_folder="dist", static_url_path="")
app.json.sort_keys = False  # 不要对json排序

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)  # 只显示 ERROR 级别及以上的日志（隐藏 INFO 和 DEBUG）
logger = get_logger(blocked_loggers=["DEBUG", "INFO_MSG"])

CORS(app, supports_credentials=True)  # 启用跨域支持
sock = Sock(app)  # 初始化Flask sock

custom_git_path = os.path.join("environments", "MinGit", "cmd", "git.exe")
if os.path.exists(custom_git_path):
    git_path = custom_git_path
else:
    git_path = "git"

logger.info(f"Git path: {git_path}")

# 默认用户信息
user_info = {
    # webUI默认账户密码
    "account": "eridanus",
    "password": "f6074ac37e2f8825367d9ae118a523abf16924a86414242ae921466db1e84583",
    # 机器人好友和群聊数量
    "friends": 0,
    "groups": 0,
}

#ip白名单，便于不看文档的用户和远程开发调试使用
ip_whitelist = ["127.0.0.1","192.168.195.128"]

# 用户信息文件
user_file = "../user_info.yaml"

# 会话信息字典（token跟expires）
auth_info = {}

# 会话有效时长，秒数为单位（暂时只对webui生效）
auth_duration = 720000
# 可用的git源
REPO_SOURCES = [
    "https://ghfast.top/https://github.com/avilliai/Eridanus.git",
    "https://mirror.ghproxy.com/https://github.com/avilliai/Eridanus",
    "https://github.moeyy.xyz/https://github.com/avilliai/Eridanus",
    "https://github.com/avilliai/Eridanus.git",
    "https://gh.llkk.cc/https://github.com/avilliai/Eridanus.git",
    "https://gitclone.com/github.com/avilliai/Eridanus.git"
]


# 配置文件路径
def get_plugin_description(plugin_dir):
    init_file = os.path.join(plugin_dir, '__init__.py')
    if not os.path.exists(init_file):
        return None
    spec = importlib.util.spec_from_file_location("plugin_init", init_file)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        return getattr(module, 'plugin_description', None)
    except Exception:
        return None


def build_yaml_file_map(run_dir):
    yaml_map = {}
    run_dir = os.path.abspath(run_dir)
    for root, _, files in os.walk(run_dir):
        for file in files:
            if not file.endswith('.yaml'):
                continue
            abs_path = os.path.join(root, file)
            rel_path = os.path.relpath(abs_path, run_dir).replace("\\", "/")
            parts = rel_path.split("/")
            if len(parts) < 2:
                continue  # 不处理 run 目录下直接放的文件
            plugin_dir = os.path.join(run_dir, parts[0])
            plugin_desc = get_plugin_description(plugin_dir)
            if not plugin_desc:
                continue  # 没有 plugin_description 就跳过
            filename = os.path.splitext(parts[-1])[0]
            key = f"{plugin_desc}.{filename}"
            yaml_map[key] = abs_path
    return yaml_map


RUN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'run'))
YAML_FILES = build_yaml_file_map(RUN_DIR)

# 初始化 YAML 解析器（支持注释）
yaml = YAML()
yaml.preserve_quotes = True

"""
读取配置
"""

"""
新旧数据合并
"""


def merge_dicts(old, new):
    """
    递归合并旧数据和新数据。
    """
    for k, v in old.items():
        logger.server(
            f"处理 key: {k}, old value: {v} old type: {type(v)}, new value: {new.get(k)} new type: {type(new.get(k))}")
        # 如果值是一个字典，并且键在新的yaml文件中，那么我们就递归地更新键值对
        if isinstance(v, dict) and k in new and isinstance(new[k], dict):
            merge_dicts(v, new[k])
        # 如果值是列表，且新旧值都是列表，则合并并去重
        elif isinstance(v, list) and k in new and isinstance(new[k], list):
            # 合并列表并去重，保留旧列表顺序
            new[k] = [item for item in v if v is not None]
        elif k in new and type(v) != type(new[k]):

            if isinstance(new[k], DoubleQuotedScalarString) or isinstance(new[k], SingleQuotedScalarString):
                v = str(v)
                new[k] = v
            elif isinstance(new[k], ScalarInt) or isinstance(v, ScalarInt):
                v = int(v)
                new[k] = v
            else:
                logger.server(f"类型冲突 key: {k}, old value type: {type(v)}, new value type: {type(new[k])}")
                logger.warning(f"旧值: {v}, 新值: {new[k]} 直接覆盖")
                new[k] = v
        # 如果键在新的yaml文件中且类型一致，则更新值
        elif k in new:
            logger.server(f"更新 key: {k}, old value: {v}, new value: {new[k]}")
            new[k] = v
        # 如果键不在新的yaml中，直接添加
        else:
            logger.server(f"移除键 key: {k}, value: {v}")


def conflict_file_dealer(old_data: dict, file_new='new_aiReply.yaml'):
    logger.info(f"冲突文件处理: {file_new}")

    old_data_yaml_str = StringIO()
    yaml.dump(old_data, old_data_yaml_str)
    old_data_yaml_str.seek(0)  # 将光标移到字符串开头，以便后续读取

    # 将 YAML 字符串加载回 ruamel.yaml 对象
    old_data = yaml.load(old_data_yaml_str)
    # 加载新的YAML文件
    with open(file_new, 'r', encoding="utf-8") as file:
        new_data = yaml.load(file)

    # 遍历旧的YAML数据并更新新的YAML数据中的相应值
    merge_dicts(old_data, new_data)

    # 把新的YAML数据保存到新的文件中，保留注释
    with open(file_new, 'w', encoding="utf-8") as file:
        yaml.dump(new_data, file)
    return True


def extract_comments(data, path="", comments_dict=None):
    if comments_dict is None:
        comments_dict = {}

    if isinstance(data, comments.CommentedMap):
        for key, value in data.items():
            new_path = f"{path}.{key}" if path else key
            # 提取行尾注释
            if key in data.ca.items and data.ca.items[key][2]:
                comment = data.ca.items[key][2].value.strip("# \n")
                comments_dict[new_path] = comment
            # 递归处理子节点
            extract_comments(value, new_path, comments_dict)

    elif isinstance(data, comments.CommentedSeq):
        for index, item in enumerate(data):
            new_path = f"{path}[{index}]"
            # 序列整体注释（如果存在）
            if data.ca.comment and data.ca.comment[0]:
                comments_dict[path] = data.ca.comment[0].value.strip("# \n")
            # 递归处理子节点
            extract_comments(item, new_path, comments_dict)

    return comments_dict


def extract_key_order(data, path="", order_dict=None):
    if order_dict is None:
        order_dict = {}

    if isinstance(data, comments.CommentedMap):
        order_dict[path] = list(data.keys())  # 记录当前层级 key 的顺序
        for key, value in data.items():
            new_path = f"{path}.{key}" if path else key
            extract_key_order(value, new_path, order_dict)

    elif isinstance(data, comments.CommentedSeq):
        # 对于序列，记录其位置
        for index, item in enumerate(data):
            new_path = f"{path}[{index}]"
            extract_key_order(item, new_path, order_dict)

    return order_dict


def load_yaml_with_comments(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.load(f)
        # 提取所有注释
        order = extract_key_order(data)
        comments = extract_comments(data)
        return {"data": data, "comments": comments, "order": order}
    except Exception as e:
        return {"error": str(e)}


def load_yaml(file_path):
    """加载 YAML 文件并返回内容及注释"""
    try:
        return load_yaml_with_comments(file_path)
    except Exception as e:
        return {"error": str(e)}


def save_yaml(file_path, data):
    """将数据保存回 YAML 文件"""

    # logger.server(f"保存文件: {file_path}")
    # logger.server(f"数据: {data}")
    return conflict_file_dealer(data["data"], file_path)


# 鉴权
def auth(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        #白名单直接放行
        if request.remote_addr in ip_whitelist:
            return func(*args, **kwargs)
        global auth_info
        recv_token = request.cookies.get('auth_token')
        try:
            if auth_info[recv_token] < int(time.time()):  # 如果存在token且过期
                return jsonify({"error": "Unauthorized"})
        except:  # 不存在token
            return jsonify({"error": "Unauthorized"})
        return func(*args, **kwargs)

    return wrapper


@app.route("/api/load/<filename>", methods=["GET"])
@auth
def load_file(filename):
    """加载指定的 YAML 文件"""
    if filename not in YAML_FILES:
        return jsonify({"error": "文件名错误"})

    file_path = YAML_FILES[filename]
    if not os.path.exists(file_path):
        return jsonify({"error": "文件不存在"})

    data_with_comments = load_yaml(file_path)
    rtd = jsonify(data_with_comments)

    return rtd


@app.route("/api/save/<filename>", methods=["POST"])
@auth
def save_file(filename):
    """接收前端数据并保存到 YAML 文件"""
    if filename not in YAML_FILES:
        return jsonify({"error": "文件名错误"})

    file_path = YAML_FILES[filename]
    if not os.path.exists(file_path):
        return jsonify({"error": "文件不存在"})

    data = request.json  # 获取前端发送的 JSON 数据
    if not data:
        return jsonify({"error": "无效数据"})

    result = save_yaml(file_path, data)
    if result:
        return jsonify({"message": "文件保存成功"})
    else:
        return jsonify(result)


@app.route("/api/sources", methods=["GET"])
@auth
def list_sources():
    """列出所有可用的git源"""
    return jsonify(list(REPO_SOURCES))


@app.route("/api/files", methods=["GET"])
@auth
def list_files():
    """列出所有可用的 YAML 文件"""
    return jsonify({"files": list(YAML_FILES.keys())})


@app.route("/api/pull", methods=["POST"])
@auth
def pull_eridanus():
    """从仓库拉取eridanus(未完成)"""
    return jsonify({"message": "success"})


@app.route("/api/clone", methods=["POST"])
@auth
def clone_source():
    data = request.get_json()
    source_url = data.get("source")

    if not source_url:
        return jsonify({"error": "Missing source URL"})
    if os.path.exists("Eridanus"):
        return jsonify({"error": "Eridanus already exists。请删除现有Eridanus后再尝试克隆"})

    logger.server(f"开始克隆: {source_url}")
    os.system(f"{git_path} clone --depth 1 {source_url}")

    return jsonify({"message": f"开始部署 {source_url}"})


# 登录api
@app.route("/api/login", methods=['POST'])
def login():
    global auth_info
    global auth_duration
    data = request.get_json()
    # 不能给用户看
    # logger.server(data)
    if data["account"] == user_info["account"] and data["password"] == user_info["password"]:
        logger.server("webUI登录成功")
        auth_token = Fernet.generate_key().decode()  # 生成token
        auth_expires = int(time.time() + auth_duration)  # 生成过期时间
        auth_info[auth_token] = auth_expires  # 加入字典
        resp = make_response(jsonify({"message": "登录成功", "auth_token": auth_token}))
        resp.set_cookie("auth_token", auth_token)
        resp.set_cookie("auth_expires", str(auth_expires))
        return resp
    else:
        logger.error("webUI登录失败")
        return jsonify({"error": "Failed"})


# 登出api
@app.route("/api/logout", methods=['GET', 'POST'])
def logout():
    global auth_info
    recv_token = request.cookies.get('auth_token')
    try:
        del auth_info[recv_token]
        logger.server("用户登出")
        return jsonify({"message": "退出登录成功"})
    except:
        return jsonify({"error": "登录信息无效"})


# 账户修改
@app.route("/api/profile", methods=['GET', 'POST'])
@auth
def profile():
    global user_info
    global auth_info
    if request.method == 'GET':
        return jsonify({"account": user_info['account']})
    elif request.method == 'POST':
        data = request.get_json()
        logger.server(data)
        if data["account"]:
            user_info["account"] = data["account"]
        if data["password"]:
            user_info["password"] = data["password"]
            with open(user_file, 'w', encoding="utf-8") as file:
                yaml.dump(user_info, file)
        auth_info = {}  # 清空登录信息
        return jsonify({"message": "账户信息修改成功，请重新登录"})


# 用户管理
@app.route("/api/usermgr/userList", methods=["GET"])
@auth
def get_users():
    try:
        # 当前页
        current = int(request.args.get("current"))
        # 每页数量
        page_size = int(request.args.get("pageSize"))
        start = (current - 1) * page_size
        end = start + page_size
        sort_by = request.args.get("sortBy")
        sort_order = request.args.get("sortOrder")

        async def fetch_users():
            if request.args.get("user_id"):
                user_id = request.args.get("user_id")
                total_count = await get_users_count(user_id)
                result = await search_users_by_id(user_id, start, end, sort_by, sort_order)
                return total_count, result
            else:
                # 获取用户总数
                total_count = await get_users_count()
                # 获取指定范围的用户
                users = await get_users_range(start, end, sort_by, sort_order)
                return total_count, users

        total_count, users = asyncio.run(fetch_users())

        return jsonify({
            "data": users,
            "total": total_count,
            "success": True,
            "pageSize": page_size,
            "current": current,
        })
    except Exception as e:
        return jsonify({"error": f"获取用户信息失败: {e}"}), 500


# 机器人的基本信息
@app.route("/api/dashboard/basicInfo", methods=["GET"])
@auth
def basic_info():
    try:
        system_info_only = request.args.get("systemInfo")
        # 获取系统信息
        cpu_percent = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        if system_info_only:
            return jsonify({
                "systemInfo": {
                    "cpuUsage": cpu_percent,
                    "totalMemory": memory.total,
                    "usedMemory": memory.used,
                    "totalDisk": disk.total,
                    "usedDisk": disk.used
                },
            })
        # 获取好友和群聊信息
        with open(user_file, 'r', encoding="utf-8") as file:
            yaml_file = yaml.load(file)
            user_info['friends'] = yaml_file['friends']
            user_info['groups'] = yaml_file['groups']

        # 获取排行榜数据
        async def get_ranks():
            token_rank = await get_users_range(0, 10, "ai_token_record", "DESC")
            signin_rank = await get_user_signed_days()
            total_users = await get_users_count()
            return token_rank, signin_rank, total_users

        token_rank, signin_rank, total_users = asyncio.run(get_ranks())

        basic_info = {
            "systemInfo": {
                "cpuUsage": cpu_percent,
                "totalMemory": memory.total,
                "usedMemory": memory.used,
                "totalDisk": disk.total,
                "usedDisk": disk.used
            },
            "botInfo": {
                "totalUsers": total_users,
                "totalFriends": user_info['friends'],
                "totalGroups": user_info['groups']
            },
            "ranks": {
                "tokenRank": token_rank,
                "signInRank": signin_rank
            }
        }
        return jsonify(basic_info)
    except Exception as e:
        return jsonify({"error": f"获取基本信息失败: {e}"})


# API外的路由（404）完全交给React前端处理,根路由都不用了
@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, 'index.html')


BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 普通运行环境

UPLOAD_FOLDER = os.path.join(BASE_DIR, "websources", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # 确保目录存在


@app.route("/api/move_file", methods=["POST"])
@auth
def move_file():
    """移动本地文件到可访问目录，并返回 URL"""
    data = request.json
    file_path = data.get("path")

    if not file_path:
        return jsonify({"error": "Missing file path"})

    if file_path.startswith("file://"):
        file_path = file_path[7:]  # 去掉 "file://"

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"})

    try:
        # 确保文件不会覆盖已有文件
        filename = os.path.basename(file_path)
        dest_path = os.path.join(UPLOAD_FOLDER, filename)

        logger.server(f"目标路径: {dest_path} 原始路径: {file_path}")
        shutil.move(file_path, dest_path)  # 移动文件

        # 生成可访问的 URL
        relative_path = os.path.relpath(dest_path, app.static_folder)  # 计算相对路径
        file_url = f"/{relative_path}"  # Flask 已去掉 static_url_path，所以直接返回相对路径
        return jsonify({"url": file_url})

    except Exception as e:
        return jsonify({"error": str(e)})


#
# 考虑到webui对话需要保存聊天记录，但是媒体文件不能保存到浏览器缓存，以后参考上面移动文件到目录下的操作，所有聊天文件通过webUI的一个文件管理器管理(todo)

@app.route("/api/chat/file", methods=["GET"])
@auth
def get_file():
    # data = request.json
    file_path = request.args.get("path")

    if not file_path:
        return jsonify({"error": "缺少文件路径"})

    if file_path.startswith("file://"):
        file_path = file_path[7:]  # 去掉 "file://"

    if not os.path.exists(file_path):
        return jsonify({"error": "文件不存在"})

    try:
        return send_file(file_path)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/api/chat/music", methods=["POST"])
@auth
def get_music():
    try:
        response = httpx.post(
            "https://ss.xingzhige.com/music_card/card",
            json = request.json
        )
        # 解析返回的JSON数据
        result = response.json()
        music_data = result['meta']['music']
        return jsonify(music_data)
    except Exception as e:
        return jsonify({"error": f"请求时出错: {str(e)}"})

clients = set()


# WebSocket路由
@sock.route('/api/ws')
def handle_websocket(ws):
    global auth_info
    logger.server("WebSocket 客户端已连接")
    clients.add(ws)
    try:
        # 对非本地的访问鉴权
        try:
            if request.remote_addr not in ip_whitelist:
                recv_token = request.args.get('auth_token')
                if auth_info[recv_token] > int(time.time()):
                    logger.server("WebSocket 客户端鉴权成功")
        except:
            raise ValueError("WebSocket 客户端鉴权失败")
        while True:
            # 接收来自前端的消息
            message = ws.receive()
            logger.server(f"收到前端消息: {message} {type(message)}")
            message = json.loads(message)
            if "echo" in message:
                for client in list(clients):
                    try:
                        client.send(json.dumps({'status': 'ok',
                                                'retcode': 0,
                                                'data': {'message_id': 1253451396},
                                                'message': '',
                                                'wording': '',
                                                'echo': message['echo']}))
                    except Exception:
                        clients.discard(client)
                        # 获取前端消息的id
            time_now = int(time.time())

            # 是否@，有些指令不能用@
            # isat = message[0]["isat"] if "id" in message[0] else True
            # 删除消息中的id和isat字段
            # 删除消息中的id和isat字段
            if "id" in message:
                message_id = message["id"]
                isat = message["isat"]
                del message["isat"]
                del message["id"]
                message = [message]
                if isat:
                    message.insert(0, {'type': 'at', 'data': {'qq': '1000000', 'name': 'Eridanus'}})
            else:
                message_id = time_now

            # logger.server(message, type(message))

            onebot_event = {
                'self_id': 1000000,
                'user_id': 111111111,
                'time': time_now,
                'message_id': message_id,
                'real_id': 1253451396,
                'message_seq': 1253451396,
                'message_type': 'group',
                'sender':
                    {'user_id': 111111111, 'nickname': '主人', 'card': '', 'role': 'member', 'title': ''},
                'raw_message': "",
                'font': 14,
                'sub_type': 'normal',
                'message': message,
                'message_format': 'array',
                'post_type': 'message',
                'group_id': 879886836}

            def send_mes(onebot_event):
                event_json = json.dumps(onebot_event, ensure_ascii=False)

                # 发送给所有连接的客户端（后端）
                for client in list(clients):
                    try:
                        if client != ws:  # 避免回传给前端
                            client.send(event_json)
                    except Exception:
                        clients.discard(client)

                logger.server(f"已发送 OneBot v11 事件: {event_json}")
            # def is_valid_messages_structure(data):
            #     # 检查字典是否包含 message 键
            #     if not isinstance(data, dict) or 'message' not in data:
            #         return False

            #     # 检查 message 是否包含 action 和 params
            #     message = data.get('message')
            #     if not isinstance(message, dict) or 'action' not in message or 'params' not in message:
            #         return False

            #     # 检查 action 是否为 send_group_forward_msg
            #     if message['action'] != 'send_group_forward_msg':
            #         return False

            #     # 检查 params 是否包含 messages
            #     params = message.get('params')
            #     if not isinstance(params, dict) or 'messages' not in params:
            #         return False

            #     # 检查 messages 是否为列表
            #     messages = params.get('messages')
            #     if not isinstance(messages, list):
            #         return False
            #     # 检查 messages 中的每个元素是否为 node 类型
            #     for msg in messages:
            #         if not isinstance(msg, dict) or 'type' not in msg or msg['type'] != 'node':
            #             return False
            #         # 进一步检查 node 是否包含 data 且 data 包含 content
            #         if 'data' not in msg or not isinstance(msg['data'], dict):
            #             return False
            #         if 'content' not in msg['data'] or not isinstance(msg['data']['content'], list):
            #             return False

            #     return True
            # if is_valid_messages_structure(onebot_event):
            #     """
            #     对Node消息进行处理
            #     """
            #     back_event = onebot_event.copy()
            #     for node in onebot_event['message']["params"]["messages"]:
            #         content=node['data']['content']
            #         back_event["message"]["action"] ="send_group_msg"
            #         back_event['message']["params"]["message"] = content
            #         send_mes(back_event)
            # else:
            send_mes(onebot_event)
    except Exception as e:
        logger.server(f"WebSocket事件: {e}")
    finally:
        # 总有人看见红色就害怕
        # logger.server("WebSocket 客户端断开连接")
        clients.discard(ws)


# 启动webUI
def start_webui():
    # 初始化用户登录信息
    try:
        with open(user_file, 'r', encoding="utf-8") as file:
            yaml_file = yaml.load(file)
            user_info['account'] = yaml_file['account']
            user_info['password'] = yaml_file['password']
            user_info['friends'] = yaml_file['friends']
            user_info['groups'] = yaml_file['groups']
        logger.server(f"登录信息读取成功。初始用户名和密码均为 {user_info['account']} ")
        logger.server("请访问 http://localhost:5007 登录")
        logger.server("请访问 http://localhost:5007 登录")
        logger.server("请访问 http://localhost:5007 登录")
    except:
        logger.warning("登录信息读取失败，已恢复默认。默认用户名/密码：eridanus")
        with open(user_file, 'w', encoding="utf-8") as file:
            yaml.dump(user_info, file)

    app.run(host="0.0.0.0", port=5007)
# 启动Eridanus并捕获输出，反馈到前端。
# 不会写，不写！

