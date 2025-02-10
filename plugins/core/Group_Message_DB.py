import aiosqlite
import json

import asyncio

from plugins.core.aiReplyHandler.gemini import gemini_prompt_elements_construct

DB_NAME = "data/dataBase/group_message.db"


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                group_id INTEGER PRIMARY KEY,
                data TEXT NOT NULL
            )
        """)
        await db.commit()


async def add_to_group(group_id: int,message):
    new_entry =message
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT data FROM groups WHERE group_id = ?", (group_id,))
        row = await cursor.fetchone()

        if row:
            data_list = json.loads(row[0])
            data_list.append(new_entry)
            await db.execute("UPDATE groups SET data = ? WHERE group_id = ?", (json.dumps(data_list), group_id))
        else:
            await db.execute("INSERT INTO groups (group_id, data) VALUES (?, ?)", (group_id, json.dumps([new_entry])))

        await db.commit()


async def get_last_20(group_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT data FROM groups WHERE group_id = ?", (group_id,))
        row = await cursor.fetchone()

        if row:
            data_list = json.loads(row[0])
            return data_list[-20:]  # 返回最后 20 条
        return []
async def get_last_20_and_convert_to_prompt(group_id: int,data_length=20,prompt_standard="gemini",bot=None,event=None):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT data FROM groups WHERE group_id = ?", (group_id,))
        row = await cursor.fetchone()

        if row:
            data_list = json.loads(row[0])
            data_li=data_list[-data_length:]
            final_list=[]

            for i in data_li:
                if prompt_standard=="gemini":
                    i["message"].insert(0,{"text": f"本条及接下来的消息为群聊上下文背景消息，消息发送者为 {i['user_name']} id为{i['user_id']} "})
                    p=await gemini_prompt_elements_construct(i["message"],bot=bot,event=event)
                    final_list.append(p)
                    final_list.append({"role": "model","parts":{"text":"群聊消息已记录"}})
            return final_list
        return []
asyncio.run(init_db())

