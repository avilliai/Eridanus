import aiosqlite
import json
import asyncio
import time  # 导入 time 模块

from plugins.core.aiReplyHandler.gemini import gemini_prompt_elements_construct

DB_NAME = "data/dataBase/group_message.db"
MAX_RETRIES = 5  # 最大重试次数
INITIAL_DELAY = 2  # 初始延迟时间 (秒)


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
                raise
    raise Exception(f"Max retries reached. Database still locked after {MAX_RETRIES} attempts.")


async def init_db():
    """初始化数据库，检查并添加 processed_message 字段"""
    async with aiosqlite.connect(DB_NAME) as db:
        try:
            # 创建表（如果不存在）
            await execute_with_retry(db, """
                CREATE TABLE IF NOT EXISTS group_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # **检查并添加 processed_message 字段**
            cursor = await db.execute("PRAGMA table_info(group_messages)")
            columns = [row[1] for row in await cursor.fetchall()]
            if "processed_message" not in columns:
                await db.execute("ALTER TABLE group_messages ADD COLUMN processed_message TEXT;")
                await db.commit()
                print("✅ 添加 processed_message 字段成功！")

            # 启用 WAL 模式，提高并发性能
            await db.execute("PRAGMA journal_mode=WAL;")
            await db.commit()

        except Exception as e:
            print(f"Error initializing database: {e}")


asyncio.run(init_db())


async def add_to_group(group_id: int, message):
    """向群组添加消息（插入 group_messages 表，processed_message 为空）"""
    async with aiosqlite.connect(DB_NAME) as db:
        try:
            await execute_with_retry(
                db,
                "INSERT INTO group_messages (group_id, message, processed_message) VALUES (?, ?, NULL)",
                (group_id, json.dumps(message))
            )
            await db.commit()
        except Exception as e:
            print(f"Error adding to group {group_id}: {e}")


async def get_last_20_and_convert_to_prompt(group_id: int, data_length=20, prompt_standard="gemini", bot=None, event=None):
    """获取群组最后 20 条消息并转换为 prompt，优先使用缓存的 processed_message"""
    async with aiosqlite.connect(DB_NAME) as db:
        try:
            cursor = await db.execute(
                "SELECT id, message, processed_message FROM group_messages WHERE group_id = ? ORDER BY timestamp DESC LIMIT ?",
                (group_id, data_length)
            )
            rows = await cursor.fetchall()

            final_list = []
            for row in rows:
                message_id, raw_message, processed_message = row
                raw_message = json.loads(raw_message)

                if processed_message:  # 直接使用缓存
                    final_list.append(json.loads(processed_message))
                else:
                    # 处理消息并缓存
                    raw_message["message"].insert(0, {"text": f"本条及接下来的消息为群聊上下文背景消息，消息发送者为 {raw_message['user_name']} id为{raw_message['user_id']} "})
                    processed = await gemini_prompt_elements_construct(raw_message["message"], bot=bot, event=event)
                    final_list.append(processed)
                    final_list.append({"role": "model", "parts": {"text": "群聊消息已记录"}})

                    # 更新数据库
                    await execute_with_retry(
                        db,
                        "UPDATE group_messages SET processed_message = ? WHERE id = ?",
                        (json.dumps(processed), message_id)
                    )
                    await db.commit()

            return final_list

        except Exception as e:
            print(f"Error getting last 20 and converting to prompt for group {group_id}: {e}")
            return []
