import aiosqlite
import asyncio
import threading
import requests

from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import calendar

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import time

DATABASE = "data/dataBase/wifeyouwant.db"  # 修改路径为小写

# 初始化数据库表结构
async def initialize_db():
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

async def PIL_lu_maker(today , target_id):
    #print('进入图片制作')
    year, month,day= today.year, today.month ,today.day
    current_year_month = f'{year}_{month}'
    lu_list=await query_group_users(target_id, current_year_month)
    #print('获取🦌列表')

    lu_font_1000 = ImageFont.truetype("data/pictures/wife_you_want_img/方正吕建德字体简体.ttf", 15)
    lu_font_100 = ImageFont.truetype("data/pictures/wife_you_want_img/方正吕建德字体简体.ttf", 20)
    lu_font_10 = ImageFont.truetype("data/pictures/wife_you_want_img/方正吕建德字体简体.ttf", 25)
    lu_font = ImageFont.truetype("data/pictures/wife_you_want_img/方正吕建德字体简体.ttf", 30)

    #print(lu_list)
    month_days = calendar.monthrange(year, month)[1]
    lu_list_lu=['1000']
    lu_list_bulu = ['1000']
    for lu in lu_list:
        if lu[1] == 1:
            lu_list_lu.append(lu[0])
        elif lu[1] == 2:
            lu_list_bulu.append(lu[0])
    canvas_width, canvas_height = 800, 600
    #print(lu_list_lu,lu_list_bulu)
    # 创建画布
    #print('创建画布')
    canvas = Image.new("RGB", (canvas_width, canvas_height), "white")
    draw = ImageDraw.Draw(canvas)

    # 加载标题字体和日文字体
    try:
        title_font = ImageFont.truetype("data/pictures/wife_you_want_img/方正吕建德字体简体.ttf", 40)  # 标题字体
        day_font = ImageFont.truetype("data/pictures/wife_you_want_img/方正吕建德字体简体.ttf", 30)  # 日字体
    except IOError:
        title_font = ImageFont.load_default()  # 如果字体加载失败，使用默认字体
        day_font = ImageFont.load_default()

    # 写标题
    title = f"{today.strftime('%Y年%m月')}的开LU计划"
    title_bbox = draw.textbbox((0, 0), title, font=title_font)  # 获取文本边界框
    title_x = (canvas_width - (title_bbox[2] - title_bbox[0])) // 2
    draw.text((title_x, 20), title, fill="black", font=title_font)

    # 加载背景图片
    #print('加载背景图片')
    image_path = "data/pictures/wife_you_want_img/background_LU.jpg"  # 图片文件路径（需确保存在）
    try:
        background = Image.open(image_path)
        background = background.resize((100, 100))
    except IOError:
        #print("背景图片加载失败，使用填充色")
        background = None

    image_path_check = 'data/pictures/wife_you_want_img/correct-copy.png'
    dui_check = Image.open(image_path_check)
    dui_check = dui_check.resize((40, 40))

    image_path_check_cuo = 'data/pictures/wife_you_want_img/cuo.png'
    cuo_check = Image.open(image_path_check_cuo)
    cuo_check = cuo_check.resize((40, 40))

    # 日历起始位置和单元格大小
    calendar_start_x = 50
    calendar_start_y = 100
    cell_width = 100
    cell_height = 100

    now = datetime.now()
    # 绘制日历
    #print('绘制日历')
    for day in range(1, month_days + 1):
        # 计算当前日期的单元格位置
        #print(day)

        first_day_of_month = datetime(now.year, now.month, 1)
        day_of_week = first_day_of_month.weekday()
        col = (day - 1 + day_of_week) % 7
        row = (day - 1 + day_of_week) // 7
        #print(col)
        x = calendar_start_x + col * cell_width
        y = calendar_start_y + row * cell_height

        # 绘制背景图片
        if background:
            canvas.paste(background, (x, y), background.convert("RGBA"))
        else:
            draw.rectangle([x, y, x + cell_width, y + cell_height], fill="#f0f0f0", outline="black")

        for day_check_lu in lu_list_lu:
            for day_check_bulu in lu_list_bulu:
                #print(day,day_check_lu,day_check_bulu)
                x_re = x
                y_re = y + 60
                #print(day_check,day)
                if f'{day}' == f'{day_check_bulu}':
                    canvas.paste(cuo_check, (x_re, y_re), cuo_check.convert("RGBA"))
                elif f'{day}' == f'{day_check_lu}':
                    canvas.paste(dui_check, (x_re, y_re), dui_check.convert("RGBA"))

        # 绘制日期文字

        day_text = str(day)
        text_bbox = draw.textbbox((0, 0), day_text, font=day_font)  # 获取文字边界框
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = x + (cell_width - text_width) // 1.5
        text_y = y + (cell_height - text_height) // 5
        draw.text((text_x, text_y), day_text, fill="black", font=day_font)

        times = await manage_group_status('lu', f'{year}_{month}_{day}', target_id)
        if times >= 1000:
            lu_font = lu_font_1000
        elif times >= 100:
            lu_font = lu_font_100
        elif times >= 10:
            lu_font = lu_font_10
        else:
            lu_font = lu_font
        if times not in {0,1}:
            draw.text((int(x + (cell_width - text_width) // 1.5), int(y + (cell_height - text_height) // 1.2)), f'×{times}', fill="red", font=lu_font)

    # 保存并展示日历
    #print('保存并展示日历')
    #canvas.show()  # 显示图片
    path_img=f"data/pictures/cache/lulululu{int(time.time())}.png"
    canvas.save(path_img)  # 保存图片为文件

    try:
        canvas.close()
        del canvas
        import gc
        gc.collect()
    except:
        pass
    return path_img


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
    target_id=1270858640
    current_date=datetime.today()
    asyncio.run(PIL_lu_maker(current_date, target_id))
