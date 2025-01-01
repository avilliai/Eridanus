import asyncio
import os
import json
import aiosqlite
import httpx

from ruamel.yaml import YAML


yaml = YAML(typ='safe')
with open('config/api.yaml', 'r', encoding='utf-8') as f:
    local_config = yaml.load(f)
if local_config["llm"]["model"]=="gemini":
    DATABASE_FILE = "data/dataBase/conversation.db"
else:
    DATABASE_FILE = "data/dataBase/openai_conversation.db"

# --- 异步数据库操作 ---

async def init_db():
    """初始化数据库"""
    async with aiosqlite.connect(DATABASE_FILE) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS conversation_history (
                user_id INTEGER PRIMARY KEY,
                history TEXT
            )
        """)
        await db.commit()

async def get_user_history(user_id):
    """获取用户历史对话"""
    async with aiosqlite.connect(DATABASE_FILE) as db:
        async with db.execute("SELECT history FROM conversation_history WHERE user_id = ?", (user_id,)) as cursor:
            result = await cursor.fetchone()
            if result:
                return json.loads(result[0])
            else:
                return []

async def update_user_history(user_id, history):
    """更新用户历史对话"""
    async with aiosqlite.connect(DATABASE_FILE) as db:
        await db.execute("INSERT OR REPLACE INTO conversation_history (user_id, history) VALUES (?, ?)",
                       (user_id, json.dumps(history)))
        await db.commit()
async def delete_user_history(user_id):
    """删除指定用户的聊天记录"""
    async with aiosqlite.connect(DATABASE_FILE) as db:
        await db.execute("DELETE FROM conversation_history WHERE user_id = ?", (user_id,))
        await db.commit()
async def clear_all_history():
    """清理所有用户的聊天记录"""
    async with aiosqlite.connect(DATABASE_FILE) as db:
        await db.execute("DELETE FROM conversation_history")
        await db.commit()
        print("所有用户的对话记录已清理。")
asyncio.run(init_db())