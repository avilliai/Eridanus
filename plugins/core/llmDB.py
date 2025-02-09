import asyncio
import os
import json
import aiosqlite
import httpx
import re
from PIL import Image
import base64
import html

from ruamel.yaml import YAML


yaml = YAML(typ='safe')
with open('config/api.yaml', 'r', encoding='utf-8') as f:
    local_config = yaml.load(f)
if local_config["llm"]["model"]=="gemini":
    DATABASE_FILE = "data/dataBase/conversation.db"
else:
    DATABASE_FILE = "data/dataBase/openai_conversation.db"

async def use_folder_chara(file_name):
    full_path = f"data/system/chara/{file_name}"
    if file_name.endswith((".txt", ".json")):
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    elif file_name.endswith((".jpg", ".jpeg", ".png")):
        return silly_tavern_card(full_path, clear_html=True)
        
async def get_folder_chara():
    chara_list =  [f for f in os.listdir('data/system/chara')]
    return "\n".join(chara_list)

def clean_invalid_characters(s, clear_html=False):
    """
    清理字符串中的无效控制字符，并根据需要移除HTML标签及其内容，以及前面可能存在的'xxx:'或'xxx：'前缀。
    """
    cleaned = ''.join(c for c in s if ord(c) >= 32 or c in ('\t', '\n', '\r'))
    if clear_html:
        cleaned = html.unescape(cleaned)
        cleaned = re.sub(r'<[^>]+>.*?</[^>]+>', '', cleaned, flags=re.DOTALL)
        cleaned = re.sub(r'<[^>]+?/>', '', cleaned)
        cleaned = re.sub(r'^.*?(?=:|：)', '', cleaned).lstrip(':： ').lstrip()
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)
    cleaned = re.sub(r'\n\s+', '\n', cleaned)
    
    cleaned = cleaned.replace('{{user}}', '{用户}').replace('{{char}}', '{bot_name}')
    
    return cleaned.strip()

def silly_tavern_card(image_path, clear_html=False):
    """
    从给定路径的图片中提取元数据，尝试解码可能存在的base64编码的内容，并返回处理后的字符串。
    
    :param image_path: 图片文件的路径
    :param clear_html: 是否需要移除包含HTML标签及其内容及其前缀
    :return: 处理后的字符串或提示信息
    """
    chara_output = []

    try:
        with Image.open(image_path) as img:
            for key, value in img.info.items():
                if isinstance(value, str) and "chara" in key.lower():
                    try:
                        decoded = base64.b64decode(value)
                        unicode_escaped_str = decoded.decode('utf-8', errors='ignore')
                        actual_chars = unicode_escaped_str.encode('latin1').decode('unicode_escape')
                        
                        cleaned_chars = clean_invalid_characters(actual_chars, clear_html=clear_html)
                        chara_output.append(cleaned_chars)
                    except Exception as e:
                        return f"错误, 无法解码的元数据项 '{key}': {str(e)}"
        
        if not chara_output:
            return "错误, 未找到chara元数据"
        return "\n".join(chara_output)
    except Exception as e:
        return f"错误, 处理图片时出错: {str(e)}"

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

async def change_folder_chara(file_name, user_id, folder_path='data/system/chara'):
    """根据文件名更改用户的角色，并删除用户的聊天记录"""
    try:
        # 获取文件夹中的所有文件名
        folder_contents = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        
        # 检查文件名是否在文件夹内容中
        if file_name in folder_contents:
            chara = await use_folder_chara(file_name)
            if chara.startswith("错误"):
                return chara
            await delete_user_history(user_id)
            async with aiosqlite.connect('data/dataBase/charas.db') as db:
                # 更新用户的角色信息
                await db.execute("INSERT OR REPLACE INTO user_chara (user_id, chara) VALUES (?, ?)",
                                 (user_id, chara))
                await db.commit()
            
            return "人设已切换为：" + file_name
        else:
            return f"文件{file_name}不存在"
    except Exception as e:
        print(f"发生了一个错误: {e}")
        return f"发生了一个错误: {e}"
    
async def set_all_users_chara(file_name, folder_path='data/system/chara'):
    """
    将所有用户的chara字段设置为指定的file_name对应的角色信息。
    删除所有用户的聊天记录。
    """
    try:
        if not os.path.isfile(os.path.join(folder_path, file_name)):
            return f"文件{file_name}不存在"

        chara = await use_folder_chara(file_name)
        if chara.startswith("错误"):
            return chara
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

async def clear_all_users_chara():
    """
    清空chara数据库中的所有内容。
    """
    try:
        await clear_all_history()
        async with aiosqlite.connect('data/dataBase/charas.db') as db:
            await db.execute("DELETE FROM user_chara")
            await db.commit()
        return "所有用户的人设已清空"
    except Exception as e:
        print(f"发生了一个错误: {e}")
        return f"发生了一个错误: {e}"

async def clear_user_chara(user_id):
    """
    删除指定user_id的数据，包括chara字段。
    
    参数:
    - user_id: 要删除数据的用户的ID。
    返回:
    - 操作结果的消息字符串。
    """
    try:
        await delete_user_history(user_id)
        async with aiosqlite.connect('data/dataBase/charas.db') as db:
            await db.execute("DELETE FROM user_chara WHERE user_id = ?", (user_id,))
            await db.commit()
            
        return f"用户ID为 {user_id} 的人设已删除"
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
