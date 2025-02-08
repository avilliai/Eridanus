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

async def use_folder_chara(file_name):
    full_path = f"config/chara/{file_name}"
    if file_name.endswith(".txt"):
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
        
async def get_folder_chara():
    chara_list =  [f for f in os.listdir('config/chara')]
    return "\n".join(chara_list)

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
        
async def init_charas_db():
    """初始化角色数据库"""
    async with aiosqlite.connect('data/dataBase/charas.db') as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_chara (
                user_id INTEGER PRIMARY KEY,
                chara TEXT
            )
        """)
        await db.commit()
        
asyncio.run(init_charas_db())

async def change_folder_chara(file_name, user_id, folder_path='config/chara'):
    """根据文件名更改用户的角色，并删除用户的聊天记录"""
    try:
        # 获取文件夹中的所有文件名
        folder_contents = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        
        # 检查文件名是否在文件夹内容中
        if file_name in folder_contents:
            await delete_user_history(user_id)
            chara = await use_folder_chara(file_name)
            async with aiosqlite.connect('data/dataBase/charas.db') as db:
                # 更新用户的角色信息
                await db.execute("INSERT OR REPLACE INTO user_chara (user_id, chara) VALUES (?, ?)",
                                 (user_id, chara))
                await db.commit()
            
            return "历史记录已清理，人设已切换为：" + file_name
        else:
            return f"文件{file_name}不存在"
    except Exception as e:
        print(f"发生了一个错误: {e}")
        return f"发生了一个错误: {e}"
    
async def set_all_users_chara(file_name, folder_path='config/chara'):
    """
    将所有用户的chara字段设置为指定的file_name对应的角色信息。
    不会删除任何用户的聊天记录。
    """
    try:
        if not os.path.isfile(os.path.join(folder_path, file_name)):
            return f"文件{file_name}不存在"

        chara = await use_folder_chara(file_name)
        await clear_all_history()

        async with aiosqlite.connect('data/dataBase/charas.db') as db:
            cursor = await db.execute("SELECT user_id FROM user_chara")
            all_users = await cursor.fetchall()
            
            for user in all_users:
                user_id = user[0]
                await db.execute("INSERT OR REPLACE INTO user_chara (user_id, chara) VALUES (?, ?)",
                                 (user_id, chara))
            
            await db.commit()
        
        return "所有用户的人设已切换为：" + file_name
    except Exception as e:
        print(f"发生了一个错误: {e}")
        return f"发生了一个错误: {e}"
    
async def read_chara(user_id, chara_str): # 这里的chara_str是一个字符串，表示用户默认的角色
    """读取用户的角色信息，如果不存在则设置默认值"""
    if not isinstance(chara_str, str):
        raise ValueError("chara_str 必须是字符串类型")

    async with aiosqlite.connect('data/dataBase/charas.db') as db:
        cursor = await db.execute("SELECT chara FROM user_chara WHERE user_id = ?", (user_id,))
        result = await cursor.fetchone()
        if result is None:
            await db.execute("INSERT INTO user_chara (user_id, chara) VALUES (?, ?)",
                             (user_id, chara_str))
            await db.commit()
            return chara_str
        else:
            return result[0]

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