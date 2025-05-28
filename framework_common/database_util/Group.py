import aiosqlite
import json
import asyncio
import redis
import time

from developTools.utils.logger import get_logger
from run.ai_llm.service.aiReplyHandler.gemini import gemini_prompt_elements_construct
from run.ai_llm.service.aiReplyHandler.openai import prompt_elements_construct, prompt_elements_construct_old_version

DB_NAME = "data/dataBase/group_messages.db"
def is_running_in_docker():
    return os.path.exists("/.dockerenv") or os.environ.get("IN_DOCKER") == "1"

if is_running_in_docker():
    REDIS_URL = "redis://redis:6379/0"
else:
    REDIS_URL = "redis://localhost"
REDIS_CACHE_TTL = 60  # 秒

logger = get_logger()

redis_client = None
import os
import subprocess
import platform
import zipfile

REDIS_EXECUTABLE = "redis-server.exe"
REDIS_ZIP_PATH = os.path.join("data", "Redis-x64-5.0.14.1.zip")
REDIS_FOLDER = os.path.join("data", "redis_extracted")


def extract_redis_from_local_zip():
    """从本地 zip 解压 Redis 到指定目录"""
    if not os.path.exists(REDIS_FOLDER):
        os.makedirs(REDIS_FOLDER)
        logger.info("📦 正在从本地压缩包解压 Redis...")
        with zipfile.ZipFile(REDIS_ZIP_PATH, 'r') as zip_ref:
            zip_ref.extractall(REDIS_FOLDER)
        logger.info("✅ Redis 解压完成")


def start_redis_background():
    """在后台启动 Redis（仅支持 Windows）"""
    extract_redis_from_local_zip()
    redis_path = os.path.join(REDIS_FOLDER, REDIS_EXECUTABLE)
    if not os.path.exists(redis_path):
        logger.error(f"❌ 找不到 redis-server.exe 于 {redis_path}")
        return

    logger.info("🚀 启动 Redis 服务中...")
    subprocess.Popen([redis_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# 初始化 Redis 客户端
def init_redis():
    global redis_client
    if redis_client is not None:
        return

    try:
        redis_client = redis.StrictRedis.from_url(REDIS_URL, decode_responses=True)
        redis_client.ping()
        logger.info("✅ Redis 连接成功")
    except redis.exceptions.ConnectionError:
        logger.warning("⚠️ Redis 未运行，尝试自动启动 Redis...")
        if platform.system() == "Windows":
            start_redis_background()
            time.sleep(2)
            try:
                redis_client = redis.StrictRedis.from_url(REDIS_URL, decode_responses=True)
                redis_client.ping()
                logger.info("✅ Redis 已自动启动并连接成功")
            except Exception as e:
                logger.error(f"❌ Redis 启动失败：{e}")
                redis_client = None
        else:
            logger.error("❌ 非 Windows 系统，请手动安装并启动 Redis")
            redis_client = None


init_redis()
# ======================= 通用函数 =======================
MAX_RETRIES = 2
INITIAL_DELAY = 2


async def execute_with_retry(db, query, params=None):
    """带重试机制的数据库操作"""
    for attempt in range(MAX_RETRIES):
        try:
            if params:
                await db.execute(query, params)
            else:
                await db.execute(query)
            return
        except aiosqlite.OperationalError as e:
            if "database is locked" in str(e):
                delay = INITIAL_DELAY * (2 ** attempt)  # 指数退避
                logger.info(f"Database is locked. Retrying in {delay:.2f} seconds...")
                await asyncio.sleep(delay)
            else:
                raise
    raise Exception(f"Max retries reached. Database still locked after {MAX_RETRIES} attempts.")


# ======================= 初始化 =======================
async def init_db():
    """初始化数据库，检查并添加必要的字段"""
    async with aiosqlite.connect(DB_NAME) as db:
        try:
            await execute_with_retry(db, """
                CREATE TABLE IF NOT EXISTS group_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    processed_message TEXT,
                    new_openai_processed_message TEXT,
                    old_openai_processed_message TEXT
                )
            """)

            # WAL 模式，提高并发性能
            await db.execute("PRAGMA journal_mode=WAL;")
            await db.commit()

        except Exception as e:
            logger.warning(f"Error initializing database: {e}")


# 初始化数据库
asyncio.run(init_db())


# ======================= 添加消息 =======================
async def add_to_group(group_id: int, message, delete_after: int = 50):
    """向群组添加消息（插入数据库并更新 Redis）"""
    init_redis()
    async with aiosqlite.connect(DB_NAME) as db:
        try:
            cursor = await db.execute("SELECT COUNT(*) FROM group_messages WHERE group_id =?", (group_id,))
            count = (await cursor.fetchone())[0]

            if count >= delete_after:
                excess_count = count - delete_after + 1
                await execute_with_retry(
                    db,
                    "DELETE FROM group_messages WHERE id IN (SELECT id FROM group_messages WHERE group_id =? ORDER BY timestamp ASC LIMIT?)",
                    (group_id, excess_count)
                )
                await db.commit()

            await execute_with_retry(
                db,
                "INSERT INTO group_messages (group_id, message, processed_message, new_openai_processed_message, old_openai_processed_message) VALUES (?,?, NULL, NULL, NULL)",
                (group_id, json.dumps(message))
            )
            await db.commit()

            for k in ["gemini", "new_openai", "old_openai"]:
                redis_client.delete(f"group:{group_id}:{k}")

        except Exception as e:
            logger.info(f"Error adding to group {group_id}: {e}")
            
async def get_group_messages(group_id: int, limit: int = 50):
    """获取指定群组的指定数量消息，仅返回文本的列表"""
    try:
        query = "SELECT message FROM group_messages WHERE group_id =? ORDER BY timestamp DESC"
        params = (group_id,)
        if limit is not None:
            query += " LIMIT?"
            params += (limit,)

        async with aiosqlite.connect(DB_NAME) as db:
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            text_list = []
            for row in rows:
                try:
                    raw_message = json.loads(row[0])
                    if "message" in raw_message and isinstance(raw_message["message"], list):
                        for msg_obj in raw_message["message"]:
                            if isinstance(msg_obj, dict) and "text" in msg_obj and isinstance(msg_obj["text"], str):
                                text_list.append(msg_obj["text"])
                except (json.JSONDecodeError, KeyError):
                    pass
            return text_list
    except Exception as e:
        logger.info(f"Error getting messages for group {group_id}: {e}")
        return []


# ======================= 获取并转换消息 =======================
async def get_last_20_and_convert_to_prompt(group_id: int, data_length=20, prompt_standard="gemini", bot=None,
                                            event=None):
    """获取最近的消息并转换为指定格式的 prompt"""
    init_redis()
    cache_key = f"group:{group_id}:{prompt_standard}"

    # 尝试从 Redis 获取缓存
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # 映射不同的标准字段
    field_mapping = {
        "gemini": "processed_message",
        "new_openai": "new_openai_processed_message",
        "old_openai": "old_openai_processed_message"
    }

    if prompt_standard not in field_mapping:
        raise ValueError(f"不支持的 prompt_standard: {prompt_standard}")

    selected_field = field_mapping[prompt_standard]

    # 从数据库中获取消息
    async with aiosqlite.connect(DB_NAME) as db:
        try:
            cursor = await db.execute(
                f"SELECT id, message, {selected_field} FROM group_messages WHERE group_id = ? ORDER BY timestamp DESC LIMIT ?",
                (group_id, data_length)
            )
            rows = await cursor.fetchall()

            final_list = []
            for row in rows:
                message_id, raw_message, processed_message = row
                raw_message = json.loads(raw_message)

                # 如果已经处理过，使用缓存的消息
                if processed_message:
                    final_list.append(json.loads(processed_message))
                else:
                    raw_message["message"].insert(0, {
                        "text": f"本条消息消息发送者为 {raw_message['user_name']} id为{raw_message['user_id']} 这是参考消息，当我再次向你提问时，请正常回复我。"
                    })

                    if prompt_standard == "gemini":
                        processed = await gemini_prompt_elements_construct(raw_message["message"], bot=bot, event=event)
                        final_list.append(processed)
                    elif prompt_standard == "new_openai":
                        processed = await prompt_elements_construct(raw_message["message"], bot=bot, event=event)
                        final_list.append(processed)
                        final_list.append(
                            {"role": "assistant", "content": [{"type": "text", "text": "(群聊背景消息已记录)"}]})
                    else:
                        processed = await prompt_elements_construct_old_version(raw_message["message"], bot=bot,
                                                                                event=event)
                        final_list.append(processed)
                        final_list.append({"role": "assistant", "content": "(群聊背景消息已记录)"})

                    # 更新数据库
                    await execute_with_retry(
                        db,
                        f"UPDATE group_messages SET {selected_field} = ? WHERE id = ?",
                        (json.dumps(processed), message_id)
                    )
                    await db.commit()

            # 处理最终格式化的消息
            fl = []
            if prompt_standard == "gemini":
                all_parts = [part for entry in final_list if entry['role'] == 'user' for part in entry['parts']]
                fl.append({"role": "user", "parts": all_parts})
                fl.append({"role": "model", "parts": {"text": "嗯嗯，我记住了"}})
            else:
                all_parts = []
                all_parts_str = ""
                for entry in final_list:
                    if entry['role'] == 'user':
                        if isinstance(entry['content'], str):
                            all_parts_str += entry['content'] + "\n"
                        else:
                            for part in entry['content']:
                                all_parts.append(part)
                fl.append({"role": "user", "content": all_parts if all_parts else all_parts_str})
                fl.append({"role": "assistant", "content": "嗯嗯我记住了"})

            # 设置缓存
            redis_client.setex(cache_key, REDIS_CACHE_TTL, json.dumps(fl))
            return fl

        except Exception as e:
            logger.info(f"Error getting last 20 and converting to prompt for group {group_id}: {e}")
            return []


# ======================= 清除消息 =======================
async def clear_group_messages(group_id: int):
    """清除指定群组的所有消息"""
    init_redis()
    async with aiosqlite.connect(DB_NAME) as db:
        try:
            await execute_with_retry(
                db,
                "DELETE FROM group_messages WHERE group_id = ?",
                (group_id,)
            )
            await db.commit()
            logger.info(f"✅ 已清除 group_id={group_id} 的所有数据")

            # 清除所有 prompt 标准的缓存
            for k in ["gemini", "new_openai", "old_openai"]:
                redis_client.delete(f"group:{group_id}:{k}")

        except Exception as e:
            logger.error(f"❌ 清理 group_id={group_id} 数据时出错: {e}")
