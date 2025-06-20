import asyncio
import calendar
import time

from framework_common.manshuo_draw.manshuo_draw import manshuo_draw

from datetime import datetime

import aiosqlite
import requests
from PIL import Image, ImageDraw, ImageFont


DATABASE = "data/dataBase/wifeyouwant.db"  # 修改路径为小写

# 初始化数据库表结构
async def initialize_db():
    global DATABASE
    async with aiosqlite.connect(DATABASE) as db:
        # 创建类别表
        await db.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        ''')

        # 创建小组表，关联类别
        await db.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY,
                category_id INTEGER,
                name TEXT NOT NULL,
                FOREIGN KEY(category_id) REFERENCES categories(id)
            )
        ''')

        # 创建用户表，关联小组
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                group_id INTEGER,
                times INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY(group_id) REFERENCES groups(id)
            )
        ''')

        await db.commit()




# 添加或更新用户数据
async def add_or_update_user(category_name, group_name, username, times):
    global DATABASE
    async with aiosqlite.connect(DATABASE, timeout=10) as db:
        category = await db.execute('SELECT * FROM categories WHERE name = ?', (category_name,))
        category_row = await category.fetchone()

        # 如果没有该类别，创建该类别
        if not category_row:
            cursor = await db.execute('INSERT INTO categories (name) VALUES (?)', (category_name,))
            category_id = cursor.lastrowid
        else:
            category_id = category_row[0]

        group = await db.execute('SELECT * FROM groups WHERE category_id = ? AND name = ?', (category_id, group_name))
        group_row = await group.fetchone()

        if not group_row:
            cursor = await db.execute('INSERT INTO groups (category_id, name) VALUES (?, ?)', (category_id, group_name))
            group_id = cursor.lastrowid
        else:
            group_id = group_row[0]

        # 检查用户是否存在
        user = await db.execute('SELECT * FROM users WHERE username = ? AND group_id = ?', (username, group_id))
        user_row = await user.fetchone()

        if user_row:
            await db.execute('UPDATE users SET times =  ? WHERE id = ?', (times, user_row[0]))
        else:
            await db.execute('INSERT INTO users (username, group_id, times) VALUES (?, ?, ?)',(username, group_id, times))

        await db.commit()


async def add_or_update_user_collect(queue_check_make):
    global DATABASE
    async with aiosqlite.connect(DATABASE, timeout=10) as db:

        for user_info in queue_check_make:
            category_name, group_name, username, times=user_info[2], user_info[1], user_info[0], user_info[3]

            category = await db.execute('SELECT * FROM categories WHERE name = ?', (category_name,))
            category_row = await category.fetchone()

            # 如果没有该类别，创建该类别
            if not category_row:
                cursor = await db.execute('INSERT INTO categories (name) VALUES (?)', (category_name,))
                category_id = cursor.lastrowid
            else:
                category_id = category_row[0]

            group = await db.execute('SELECT * FROM groups WHERE category_id = ? AND name = ?', (category_id, group_name))
            group_row = await group.fetchone()

            if not group_row:
                cursor = await db.execute('INSERT INTO groups (category_id, name) VALUES (?, ?)', (category_id, group_name))
                group_id = cursor.lastrowid
            else:
                group_id = group_row[0]

            # 检查用户是否存在
            user = await db.execute('SELECT * FROM users WHERE username = ? AND group_id = ?', (username, group_id))
            user_row = await user.fetchone()

            if user_row:
                await db.execute('UPDATE users SET times =  ? WHERE id = ?', (times, user_row[0]))
            else:
                await db.execute('INSERT INTO users (username, group_id, times) VALUES (?, ?, ?)',(username, group_id, times))
            #print(f"Updated {username}, {group_name},  {category_name} to {times}")


        await db.commit()




# 查询某个小组的用户数据，按照次数排序
async def query_group_users(category_name, group_name):
    global DATABASE
    async with aiosqlite.connect(DATABASE) as db:
        # 获取类别ID
        category = await db.execute('SELECT id FROM categories WHERE name = ?', (category_name,))
        category_row = await category.fetchone()

        if not category_row:
            return

        category_id = category_row[0]

        # 获取小组ID
        group = await db.execute('SELECT id FROM groups WHERE category_id = ? AND name = ?', (category_id, group_name))
        group_row = await group.fetchone()

        if not group_row:
            return

        group_id = group_row[0]

        # 查询该小组下所有用户，并按次数排序
        users = await db.execute('SELECT username, times FROM users WHERE group_id = ? ORDER BY times DESC',
                                 (group_id,))
        rows = await users.fetchall()

        if not rows:
            return None
        return rows

        for row in rows:
            print(f"用户名: {row[0]}, 次数: {row[1]}")


# 查询某个小组下特定用户的数据
async def query_user_data(category_name, group_name, username):
    global DATABASE
    async with aiosqlite.connect(DATABASE) as db:
        # 获取类别ID
        category = await db.execute('SELECT id FROM categories WHERE name = ?', (category_name,))
        category_row = await category.fetchone()

        if not category_row:
            return None

        category_id = category_row[0]

        # 获取小组ID
        group = await db.execute('SELECT id FROM groups WHERE category_id = ? AND name = ?', (category_id, group_name))
        group_row = await group.fetchone()

        if not group_row:
            return None

        group_id = group_row[0]

        # 获取特定用户数据
        user = await db.execute('SELECT username, times FROM users WHERE group_id = ? AND username = ?',
                                (group_id, username))
        user_row = await user.fetchone()

        if user_row:
            return user_row[1]
        else:
            return None


# 删除类别及其关联数据
async def delete_category(category_name):
    global DATABASE
    async with aiosqlite.connect(DATABASE) as db:
        # 查找类别是否存在
        category = await db.execute('SELECT id FROM categories WHERE name = ?', (category_name,))
        category_row = await category.fetchone()

        if category_row:
            # 删除类别（级联删除其关联的小组和用户）
            await db.execute('DELETE FROM categories WHERE id = ?', (category_row[0],))
            await db.commit()


# 删除组别及其关联用户
async def delete_group(category_name, group_name):
    global DATABASE
    async with aiosqlite.connect(DATABASE) as db:
        # 获取类别ID
        category = await db.execute('SELECT id FROM categories WHERE name = ?', (category_name,))
        category_row = await category.fetchone()

        if not category_row:
            return

        category_id = category_row[0]

        # 查找组别是否存在
        group = await db.execute('SELECT id FROM groups WHERE category_id = ? AND name = ?', (category_id, group_name))
        group_row = await group.fetchone()

        if group_row:
            # 删除组别（级联删除其关联用户）
            await db.execute('DELETE FROM groups WHERE id = ?', (group_row[0],))
            await db.commit()



async def manage_group_status(user_id, group_id,type,status=None):#顺序为：个人，组别和状态
    if status is None:
        context = await query_user_data(f'{type}', f'{group_id}', f"{user_id}")
        if context is None :
            await add_or_update_user(f'{type}', f'{group_id}', f"{user_id}", 0)
        return await query_user_data(f'{type}', f'{group_id}', f"{user_id}")
    else:
        await add_or_update_user(f'{type}', f'{group_id}', f"{user_id}", status)
        return await query_user_data(f'{type}', f'{group_id}', f"{user_id}")

async def manage_group_add(from_id, target_id, target_group):
    times_from=await manage_group_status(from_id, target_group, 'wife_from_Year')
    times_target=await manage_group_status(target_id, target_group, 'wife_target_Year')
    await manage_group_status(from_id, target_group, 'wife_from_Year',times_from+1)
    await manage_group_status(target_id, target_group, 'wife_target_Year',times_target+1)

    times_from=await manage_group_status(from_id, target_group, 'wife_from_month')
    times_target=await manage_group_status(target_id, target_group, 'wife_target_month')
    await manage_group_status(from_id, target_group, 'wife_from_month',times_from+1)
    await manage_group_status(target_id, target_group, 'wife_target_month',times_target+1)

    times_from=await manage_group_status(from_id, target_group, 'wife_from_week')
    times_target=await manage_group_status(target_id, target_group, 'wife_target_week')
    await manage_group_status(from_id, target_group, 'wife_from_week',times_from+1)
    await manage_group_status(target_id, target_group, 'wife_target_week',times_target+1)

    times_from=await manage_group_status(from_id, target_group, 'wife_from_day')
    times_target=await manage_group_status(target_id, target_group, 'wife_target_day')
    await manage_group_status(from_id, target_group, 'wife_from_day',times_from+1)
    await manage_group_status(target_id, target_group, 'wife_target_day',times_target+1)

async def manage_group_check(target_group,type):

    times_from= await query_group_users(f'wife_from_{type}', target_group)
    times_target=await query_group_users(f'wife_target_{type}', target_group)
    return times_from,times_target

async def PIL_lu_maker(today , target_id,target_name,type='lu',contents=None):
    #print('进入图片制作')
    year, month,day= today.year, today.month ,today.day
    current_year_month = f'{year}_{month}'
    lu_list=await query_group_users(target_id, current_year_month)
    lu_content={}
    for lu in lu_list:
        if lu[1] == 1:
            times = await manage_group_status('lu', f'{year}_{month}_{lu[0]}', target_id)
            lu_content[f'{int(lu[0])-1}']={'type':'lu','times':times}
        elif lu[1] == 2:
            lu_content[f'{int(lu[0])-1}'] = {'type': 'nolu', 'times':1}

    if type == 'lu':
        length_today = await manage_group_status('lu_length', f'{year}_{month}_{day}',target_id)
        length_total = await manage_group_status('lu_length_total', f'basic_info', target_id)
        times_total = await manage_group_status('lu_times_total', f'basic_info', target_id)
        today_times = lu_content[f'{day-1}']['times']
        content=f"[title]{today.strftime('%Y年%m月')}的开🦌计划[/title]\n今天🦌了{today_times}次，牛牛可开心了.今天牛牛一共变长了{length_today}cm\n您一共🦌了{times_total}次，现在牛牛一共{length_total}cm!!!"
    elif type == 'supple_lu':
        length_today = await manage_group_status('lu_length', f'{year}_{month}_{day}',target_id)
        length_total = await manage_group_status('lu_length_total', f'basic_info', target_id)
        times_total = await manage_group_status('lu_times_total', f'basic_info', target_id)
        content=f"[title]{today.strftime('%Y年%m月')}的开🦌计划[/title]\n您补🦌了！！！！！，今天牛牛一共变长了{length_today}cm\n您一共🦌了{times_total}次，现在牛牛一共{length_total}cm!!!"
    elif type == 'nolu':
        content = f"[title]{today.strftime('%Y年%m月')}的开🦌计划[/title]\n您今天戒鹿了，非常棒！"

    formatted_time = datetime.now().strftime("%Y年%m月%d日 %H:%M")
    draw_content=[
        {'type': 'avatar', 'subtype': 'common', 'img': [f"https://q1.qlogo.cn/g?b=qq&nk={target_id}&s=640"],'upshift': 25,
         'content': [{'name': target_name, 'time': formatted_time}, ], 'type_software': 'lu', },
        str(content),
        {'type': 'games', 'subtype': 'LuRecordMake','content': lu_content},
    ]
    img_path=await manshuo_draw(draw_content)
    return img_path



async def daily_task():
    today = datetime.today()
    weekday = today.weekday()
    month = datetime.now().month
    day = datetime.now().day
    await delete_category('wife_from_day')
    await delete_category('wife_target_day')
    if int(weekday) == 0:
        await delete_category('wife_from_week')
        await delete_category('wife_target_week')
    if int(day) == 1:
        await delete_category('wife_from_month')
        await delete_category('wife_target_month')
    print(f"每日今日老婆已重置")

# 包装一个同步任务来调用异步任务
def run_async_task():
    asyncio.run(daily_task())

def today_check_api(today_wife_api,header,num_check=None):
    if num_check is None:
        num_check=0
    headers = {'Referer': header}
    try:
        response=requests.get(today_wife_api[num_check], headers=headers)
        return response
    except:
        return today_check_api(today_wife_api,header,num_check=num_check+1)


if __name__ == '__main__':
    DATABASE = "wifeyouwant.db"  # 修改路径为小写
    target_id=1270858640
    current_date=datetime.today()
    asyncio.run(PIL_lu_maker(current_date, target_id,'manshuo'))
