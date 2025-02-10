import aiosqlite
import json
import asyncio
import time  # 导入 time 模块

from plugins.core.aiReplyHandler.gemini import gemini_prompt_elements_construct

DB_NAME = "data/dataBase/group_message.db"
MAX_RETRIES = 5  # 最大重试次数
INITIAL_DELAY = 0.1  # 初始延迟时间 (秒)

async def execute_with_retry(db, query, params=None):
    """带重试机制的数据库操作"""
    for attempt in range(MAX_RETRIES):
        try:
            if params:
                await db.execute(query, params)
            else:
                await db.execute(query)
            return  # 成功则退出循环
        except aiosqlite.OperationalError as e:
            if "database is locked" in str(e):
                delay = INITIAL_DELAY * (2 ** attempt)  # 指数退避
                print(f"Database is locked. Retrying in {delay:.2f} seconds...")
                await asyncio.sleep(delay)
            else:
                # 不是锁错误，直接抛出
                raise
    raise Exception(f"Max retries reached. Database still locked after {MAX_RETRIES} attempts.")

async def init_db():
    """初始化数据库"""
    async with aiosqlite.connect(DB_NAME) as db:
        try:
            await execute_with_retry(db, """
                CREATE TABLE IF NOT EXISTS groups (
                    group_id INTEGER PRIMARY KEY,
                    data TEXT NOT NULL
                )
            """)
            await db.commit()
        except Exception as e:
            print(f"Error initializing database: {e}")


async def add_to_group(group_id: int, message):
    """向群组添加消息"""
    new_entry = message
    async with aiosqlite.connect(DB_NAME) as db:
        try:
            cursor = await db.execute("SELECT data FROM groups WHERE group_id = ?", (group_id,))
            row = await cursor.fetchone()

            if row:
                data_list = json.loads(row[0])
                data_list.append(new_entry)
                await execute_with_retry(db, "UPDATE groups SET data = ? WHERE group_id = ?", (json.dumps(data_list), group_id))
            else:
                await execute_with_retry(db, "INSERT INTO groups (group_id, data) VALUES (?, ?)", (group_id, json.dumps([new_entry])))

            await db.commit()
        except Exception as e:
            print(f"Error adding to group {group_id}: {e}")


async def get_last_20(group_id: int):
    """获取群组最后 20 条消息"""
    async with aiosqlite.connect(DB_NAME) as db:
        try:
            cursor = await db.execute("SELECT data FROM groups WHERE group_id = ?", (group_id,))
            row = await cursor.fetchone()

            if row:
                data_list = json.loads(row[0])
                return data_list[-20:]  # 返回最后 20 条
            return []
        except Exception as e:
            print(f"Error getting last 20 messages for group {group_id}: {e}")
            return []

async def get_last_20_and_convert_to_prompt(group_id: int, data_length=20, prompt_standard="gemini", bot=None, event=None):
    """获取群组最后 20 条消息并转换为 prompt"""
    async with aiosqlite.connect(DB_NAME) as db:
        try:
            cursor = await db.execute("SELECT data FROM groups WHERE group_id = ?", (group_id,))
            row = await cursor.fetchone()

            if row:
                data_list = json.loads(row[0])
                data_li = data_list[-data_length:]
                final_list = []

                for i in data_li:
                    if prompt_standard == "gemini":
                        i["message"].insert(0, {"text": f"本条及接下来的消息为群聊上下文背景消息，消息发送者为 {i['user_name']} id为{i['user_id']} "})
                        p = await gemini_prompt_elements_construct(i["message"], bot=bot, event=event)
                        final_list.append(p)
                        final_list.append({"role": "model", "parts": {"text": "群聊消息已记录"}})
                return final_list
            return []
        except Exception as e:
            print(f"Error getting last 20 and converting to prompt for group {group_id}: {e}")
            return []
asyncio.run(init_db())

