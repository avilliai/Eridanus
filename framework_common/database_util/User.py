import json
import aiosqlite
import datetime
import asyncio
import traceback
from developTools.utils.logger import get_logger
from functools import wraps
import time

dbpath = "data/dataBase/user_management.db"

# 初始化数据库，新增注册时间字段
logger = get_logger()

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
        # 如果数据库已存在，确保字段存在（兼容旧表结构）
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



# 缓存管理
class CacheManager:
    def __init__(self, ttl=300):  # 默认缓存 5 分钟
        self.cache = {}
        self.ttl = ttl

    def get(self, key):
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return data
            else:
                del self.cache[key]
        return None

    def set(self, key, value):
        self.cache[key] = (value, time.time())

    def clear(self, key):
        if key in self.cache:
            del self.cache[key]

    def clear_all(self):
        self.cache.clear()


# 全局缓存实例
cache_manager = CacheManager(ttl=300)


# 缓存装饰器
def async_cache():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{args}"
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"缓存命中: {cache_key}")
                return cached_result
            result = await func(*args, **kwargs)
            cache_manager.set(cache_key, result)
            logger.debug(f"缓存设置: {cache_key}")
            return result

        return wrapper

    return decorator


# 添加用户时记录注册时间
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
        return f"✅ 用户 {user_id} 注册成功。"


# 更新用户信息
async def update_user(user_id, **kwargs):
    async with aiosqlite.connect(dbpath) as db:
        for key, value in kwargs.items():
            if key in ["nickname", "card", "sex", "age", "city", "permission", 'ai_token_record', 'user_portrait','portrait_update_time']:
                await db.execute(f"UPDATE users SET {key} = ? WHERE user_id = ?", (value, user_id))
        await db.commit()

    cache_key = f"get_user:({user_id},)"
    cache_manager.clear(cache_key)
    logger.info(f"✅ 用户 {user_id} 的信息已更新：{kwargs}")
    return f"✅ 用户 {user_id} 的信息已更新：{kwargs}"


# 获取用户信息（添加缓存）
@async_cache()
async def get_user(user_id, nickname="") -> User:
    try:
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
            "user_portrait": ""
        }
        async with aiosqlite.connect(dbpath) as db:
            async with db.execute("PRAGMA table_info(users);") as cursor:
                columns = await cursor.fetchall()
                column_names = [col[1] for col in columns]
                for key in default_user.keys():
                    if key not in column_names:
                        await db.execute("ALTER TABLE users ADD COLUMN ai_token_record INTEGER DEFAULT 0;")
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
                    return User(
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
                        existing_user.get('user_portrait', "")
                    )

            await db.execute("""
            INSERT INTO users (user_id, nickname, card, sex, age, city, permission, signed_days, registration_date, ai_token_record)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, default_user["nickname"], default_user["card"], default_user["sex"],
                  default_user["age"], default_user["city"], default_user["permission"],
                  default_user["signed_days"], default_user["registration_date"], default_user["ai_token_record"]))
            await db.commit()
            logger.info(f"查询的用户 {user_id} 不存在，已创建默认用户。")
            return User(
                default_user['user_id'],
                default_user['nickname'],
                default_user['card'],
                default_user['sex'],
                default_user['age'],
                default_user['city'],
                default_user['permission'],
                default_user['signed_days'],
                default_user['registration_date'],
                default_user['ai_token_record']
            )
    except:
        async with aiosqlite.connect(dbpath) as db:
            async with db.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,)) as cursor:
                if await cursor.fetchone():
                    await db.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
                    await db.commit()
        return await get_user(user_id)


# 获取签到记录
async def get_signed_days(user_id):
    async with aiosqlite.connect(dbpath) as db:
        async with db.execute("SELECT signed_days FROM users WHERE user_id = ?", (user_id,)) as cursor:
            result = await cursor.fetchone()
            return eval(result[0]) if result else []


# 记录签到
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
            cache_key = f"get_user:({user_id},)"
            cache_manager.clear(cache_key)
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