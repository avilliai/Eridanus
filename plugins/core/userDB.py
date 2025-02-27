import json
import aiosqlite
import datetime
import asyncio

from developTools.utils.logger import get_logger

dbpath="data/dataBase/user_management.db"
# 初始化数据库，新增注册时间字段
logger=get_logger()
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
            signed_days TEXT, -- 用JSON格式存储签到日期
            registration_date TEXT 
        )
        """)
        await db.commit()

# 添加用户时记录注册时间
async def add_user(user_id, nickname, card, sex="0", age=0, city="通辽", permission=0):
    async with aiosqlite.connect(dbpath) as db:
        # 检查用户是否已存在
        async with db.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,)) as cursor:
            if await cursor.fetchone():
                #logger.warning(f"用户 {user_id} 已存在，无法重复注册。")
                return f"✅ 用户 {user_id} 已存在，无法重复注册。"
        registration_date = datetime.date.today().isoformat()
        await db.execute("""
        INSERT INTO users (user_id, nickname, card, sex, age, city, permission, signed_days, registration_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, nickname, card, sex, age, city, permission, "[]", registration_date))
        await db.commit()
        #logger.info(f"用户 {user_id} 注册成功。")
        return f"✅ 用户 {user_id} 注册成功。"

# 更新用户信息
async def update_user(user_id, **kwargs):
    user = await get_user(user_id)
    if not user:
        logger.info(f"用户 {user_id} 不存在，已创建默认用户。")
        #print(f"用户 {user_id} 不存在，已创建默认用户。")
    # 更新用户信息
    async with aiosqlite.connect(dbpath) as db:
        for key, value in kwargs.items():
            if key in ["nickname", "card", "sex", "age", "city", "permission"]:
                await db.execute(f"UPDATE users SET {key} = ? WHERE user_id = ?", (value, user_id))
        await db.commit()
    logger.info(f"✅ 用户 {user_id} 的信息已更新：{kwargs}")
    return f"✅ 用户 {user_id} 的信息已更新：{kwargs}"

# 获取用户信息
async def get_user(user_id,nickname=""): #重要信息无非user_id和nickname，因此get时没有就直接创建。
    try:
        async with aiosqlite.connect(dbpath) as db:
            async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
                result = await cursor.fetchone()
                if result:
                    # 如果用户存在，直接返回信息
                    return result

            # 如果用户不存在，创建新用户
            registration_date = datetime.date.today().isoformat()
            default_user = {
                "user_id": user_id,
                "nickname": f"{nickname}",
                "card": "00000",
                "sex": "0",
                "age": 0,
                "city": "通辽",
                "permission": 0,
                "signed_days": "[]",
                "registration_date": registration_date,
            }

            await db.execute("""
            INSERT INTO users (user_id, nickname, card, sex, age, city, permission, signed_days, registration_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, default_user["nickname"], default_user["card"], default_user["sex"],
                  default_user["age"], default_user["city"], default_user["permission"],
                  default_user["signed_days"], default_user["registration_date"]))
            await db.commit()
            logger.info(f"查询的用户 {user_id} 不存在，已创建默认用户。")
            #print(f"用户 {user_id} 不存在，已创建默认用户。")
            return tuple(default_user.values())
    except:
        return await get_user(user_id) #最喜欢递归了❤
# 获取签到记录
async def get_signed_days(user_id):
    async with aiosqlite.connect(dbpath) as db:
        async with db.execute("SELECT signed_days FROM users WHERE user_id = ?", (user_id,)) as cursor:
            result = await cursor.fetchone()
            return eval(result[0]) if result else []


async def record_sign_in(user_id, nickname="DefaultUser", card="00000"):
    async with aiosqlite.connect(dbpath) as db:
        async with db.execute("SELECT signed_days FROM users WHERE user_id = ?", (user_id,)) as cursor:
            result = await cursor.fetchone()
            if not result:
                registration_date = datetime.date.today().isoformat()  # 设置注册时间
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
            return f"用户 {user_id} 签到成功，日期：{today}"
        else:
            return f"用户 {user_id} 今天已经签到过了！"

# 查找所有 permission 高于指定值的 user_id
async def get_users_with_permission_above(permission_value):
    async with aiosqlite.connect(dbpath) as db:
        async with db.execute("SELECT user_id FROM users WHERE permission > ?", (permission_value,)) as cursor:
            result = await cursor.fetchall()
            return [user[0] for user in result]  # 返回所有符合条件的 user_id 列表


asyncio.run(initialize_db())
