import asyncio
import datetime
import json
import os
import pickle
import platform
import subprocess
import time

import aiosqlite
import redis

from developTools.utils.logger import get_logger

dbpath = "data/dataBase/user_management.db"
def is_running_in_docker():
    return os.path.exists("/.dockerenv") or os.environ.get("IN_DOCKER") == "1"

if is_running_in_docker():
    REDIS_URL = "redis://redis:6379/1"
else:
    REDIS_URL = "redis://localhost/1"
REDIS_CACHE_TTL = 60  # 秒
REDIS_EXECUTABLE = "redis-server.exe"
REDIS_ZIP_PATH = os.path.join("data", "Redis-x64-5.0.14.1.zip")
REDIS_FOLDER = os.path.join("data", "redis_extracted")

logger = get_logger()
redis_client = None



def start_redis_background():
    """在后台启动 Redis（仅支持 Windows）"""
    redis_path = os.path.join(REDIS_FOLDER, REDIS_EXECUTABLE)
    if not os.path.exists(redis_path):
        logger.error(f"❌ 找不到 redis-server.exe 于 {redis_path}")
        return

    logger.info("🚀 启动 Redis 服务中...")
    subprocess.Popen([redis_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def init_redis():
    global redis_client
    if redis_client is not None:
        return
    try:
        redis_client = redis.StrictRedis.from_url(REDIS_URL)
        redis_client.ping()
        logger.info("✅ Redis 连接成功（数据库 db1）")
    except redis.exceptions.ConnectionError:
        logger.warning("⚠️ Redis 未运行，尝试自动启动 Redis...")
        if platform.system() == "Windows":
            start_redis_background()
            time.sleep(2)
            try:
                redis_client = redis.StrictRedis.from_url(REDIS_URL)
                redis_client.ping()
                logger.info("✅ Redis 已自动启动并连接成功（数据库 db1）")
            except Exception as e:
                logger.error(f"❌ Redis 启动失败：{e}")
                redis_client = None
        else:
            logger.error("❌ 非 Windows 系统，请手动安装并启动 Redis")
            redis_client = None

# 初始化数据库，新增注册时间字段
async def initialize_db():
    async with aiosqlite.connect(dbpath) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            nickname TEXT,
            card TEXT,
            sex TEXT DEFAULT '0',
            age INTEGER DEFAULT 0,
            city TEXT DEFAULT '通辽',
            permission INTEGER DEFAULT 0,
            signed_days TEXT,
            registration_date TEXT,
            ai_token_record INTEGER DEFAULT 0,
            user_portrait TEXT DEFAULT '',
            portrait_update_time TEXT DEFAULT ''
        )
        """)
        async with db.execute("PRAGMA table_info(users);") as cursor:
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns]
            if 'user_portrait' not in column_names:
                await db.execute("ALTER TABLE users ADD COLUMN user_portrait TEXT DEFAULT '';")
            if 'portrait_update_time' not in column_names:
                await db.execute("ALTER TABLE users ADD COLUMN portrait_update_time TEXT DEFAULT '';")
        await db.commit()


# User 类
class User:
    def __init__(self, user_id, nickname, card, sex, age, city, permission, signed_days, registration_date,
                 ai_token_record, user_portrait="", portrait_update_time=""):
        self.user_id = user_id
        self.nickname = nickname
        self.card = card
        self.sex = sex
        self.age = age
        self.city = city
        self.permission = permission
        self.signed_days = signed_days
        self.registration_date = registration_date
        self.ai_token_record = ai_token_record
        self.user_portrait = user_portrait
        self.portrait_update_time = portrait_update_time

    def __repr__(self):
        return (f"User(user_id={self.user_id}, nickname={self.nickname}, card={self.card}, "
                f"sex={self.sex}, age={self.age}, city={self.city}, permission={self.permission}, "
                f"signed_days={self.signed_days}, registration_date={self.registration_date}, "
                f"ai_token_record={self.ai_token_record}, user_portrait={self.user_portrait},portrait_update_time={self.portrait_update_time})")



async def add_user(user_id, nickname, card, sex="0", age=0, city="通辽", permission=0, ai_token_record=0):
    async with aiosqlite.connect(dbpath) as db:
        async with db.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,)) as cursor:
            if await cursor.fetchone():
                return f"✅ 用户 {user_id} 已存在，无法重复注册。"
        registration_date = datetime.date.today().isoformat()
        await db.execute("""
        INSERT INTO users (user_id, nickname, card, sex, age, city, permission, signed_days, registration_date, ai_token_record)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, nickname, card, sex, age, city, permission, "[]", registration_date, ai_token_record))
        await db.commit()
        # 清除缓存
        if redis_client:
            redis_client.delete(f"user:{user_id}")
        return f"✅ 用户 {user_id} 注册成功。"

# 更新用户信息
async def update_user(user_id, **kwargs):
    async with aiosqlite.connect(dbpath) as db:
        for key, value in kwargs.items():
            if key in ["nickname", "card", "sex", "age", "city", "permission", 'ai_token_record', 'user_portrait','portrait_update_time']:
                await db.execute(f"UPDATE users SET {key} = ? WHERE user_id = ?", (value, user_id))
            else:
                logger.warning(f"❌ 未知的用户字段 {key}，请检查输入是否正确。")
        await db.commit()

    # 清除缓存
    if redis_client:
        redis_client.delete(f"user:{user_id}")
    logger.info(f"✅ 用户 {user_id} 的信息已更新：{kwargs}")
    return f"✅ 用户 {user_id} 的信息已更新：{kwargs}"


async def get_user(user_id, nickname="") -> User:
    try:
        init_redis()
        cache_key = f"user:{user_id}"
        # 检查 Redis 缓存
        if redis_client:
            cached_user = redis_client.get(cache_key)
            if cached_user:
                #logger.info(f"缓存命中用户 {user_id}")
                return pickle.loads(cached_user)

        default_user = {
            "user_id": user_id,
            "nickname": f"{nickname}",
            "card": "00000",
            "sex": "0",
            "age": 0,
            "city": "通辽",
            "permission": 0,
            "signed_days": "[]",
            "registration_date": datetime.date.today().isoformat(),
            'ai_token_record': 0,
            "user_portrait": "",
            "portrait_update_time": ""
        }
        async with aiosqlite.connect(dbpath) as db:
            async with db.execute("PRAGMA table_info(users);") as cursor:
                columns = await cursor.fetchall()
                column_names = [col[1] for col in columns]
                for key in default_user.keys():
                    if key not in column_names:
                        await db.execute(f"ALTER TABLE users ADD COLUMN {key} TEXT DEFAULT '';")
                        await db.commit()
                        logger.info(f"列 {key} 已成功添加至 'users' 表中。")

            async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
                result = await cursor.fetchone()
                if result:
                    column_names = [description[0] for description in cursor.description]
                    existing_user = dict(zip(column_names, result))
                    missing_keys = [key for key in default_user if key not in existing_user]
                    if missing_keys:
                        for key in missing_keys:
                            existing_user[key] = default_user[key]
                        update_query = f"UPDATE users SET {', '.join(f'{key} = ?' for key in missing_keys)} WHERE user_id = ?"
                        update_values = [existing_user[key] for key in missing_keys] + [user_id]
                        await db.execute(update_query, update_values)
                        await db.commit()
                    user_obj = User(
                        existing_user['user_id'],
                        existing_user['nickname'],
                        existing_user['card'],
                        existing_user['sex'],
                        existing_user['age'],
                        existing_user['city'],
                        existing_user['permission'],
                        existing_user['signed_days'],
                        existing_user['registration_date'],
                        existing_user['ai_token_record'],
                        existing_user.get('user_portrait', ""),
                        existing_user.get('portrait_update_time', "")  # 修复：获取数据库中的 portrait_update_time
                    )
                    # 存储到 Redis 缓存
                    if redis_client:
                        redis_client.setex(cache_key, REDIS_CACHE_TTL, pickle.dumps(user_obj))
                    return user_obj

            await db.execute("""
            INSERT INTO users (user_id, nickname, card, sex, age, city, permission, signed_days, registration_date, ai_token_record, user_portrait, portrait_update_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, default_user["nickname"], default_user["card"], default_user["sex"],
                  default_user["age"], default_user["city"], default_user["permission"],
                  default_user["signed_days"], default_user["registration_date"], default_user["ai_token_record"],
                  default_user["user_portrait"], default_user["portrait_update_time"]))
            await db.commit()
            logger.info(f"用户 {user_id} 不在数据库中，已创建默认用户。")
            user_obj = User(
                default_user['user_id'],
                default_user['nickname'],
                default_user['card'],
                default_user['sex'],
                default_user['age'],
                default_user['city'],
                default_user['permission'],
                default_user['signed_days'],
                default_user['registration_date'],
                default_user['ai_token_record'],
                default_user['user_portrait'],
                default_user['portrait_update_time']
            )
            # 存储到 Redis 缓存
            if redis_client:
                redis_client.setex(cache_key, REDIS_CACHE_TTL, pickle.dumps(user_obj))
            return user_obj
    except Exception as e:
        logger.error(f"获取用户 {user_id} 时出错：{e}")
        async with aiosqlite.connect(dbpath) as db:
            async with db.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,)) as cursor:
                if await cursor.fetchone():
                    await db.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
                    await db.commit()
        # 清除缓存
        if redis_client:
            redis_client.delete(f"user:{user_id}")
        return await get_user(user_id)


# 获取签到记录
async def get_signed_days(user_id):
    async with aiosqlite.connect(dbpath) as db:
        async with db.execute("SELECT signed_days FROM users WHERE user_id = ?", (user_id,)) as cursor:
            result = await cursor.fetchone()
            return eval(result[0]) if result else []

# 记录签到并更新缓存
async def record_sign_in(user_id, nickname="DefaultUser", card="00000"):
    async with aiosqlite.connect(dbpath) as db:
        async with db.execute("SELECT signed_days FROM users WHERE user_id = ?", (user_id,)) as cursor:
            result = await cursor.fetchone()
            if not result:
                registration_date = datetime.date.today().isoformat()
                await db.execute("""
                INSERT INTO users (user_id, nickname, card, signed_days, registration_date)
                VALUES (?, ?, ?, ?, ?)
                """, (user_id, nickname, card, "[]", registration_date))
                await db.commit()
                print(f"用户 {user_id} 不存在，已创建新用户。")
                signed_days = []
            else:
                signed_days = json.loads(result[0])

        today = datetime.date.today().isoformat()
        if today not in signed_days:
            signed_days.append(today)
            signed_days.sort()
            await db.execute("UPDATE users SET signed_days = ? WHERE user_id = ?", (json.dumps(signed_days), user_id))
            await db.commit()
            # 清除缓存
            if redis_client:
                redis_client.delete(f"user:{user_id}")
            return f"用户 {user_id} 签到成功，日期：{today}"
        else:
            return f"用户 {user_id} 今天已经签到过了！"

# 查找权限高于指定值的用户
async def get_users_with_permission_above(permission_value):
    async with aiosqlite.connect(dbpath) as db:
        async with db.execute("SELECT user_id FROM users WHERE permission > ?", (permission_value,)) as cursor:
            result = await cursor.fetchall()
            return [user[0] for user in result]



asyncio.run(initialize_db())
