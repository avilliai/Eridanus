from bilibili_api import hot, sync,Credential
import os
import requests
import platform
import subprocess
import re
import aiofiles
import httpx
from typing import Optional
import asyncio
import os.path
from PIL import Image, ImageDraw, ImageFont
import yaml
import inspect
from io import BytesIO
from plugins.resource_search_plugin.Link_parsing.core.login_core import ini_login_Link_Prising


def bili_init():
    BILIBILI_HEADER = {
        'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 '
            'Safari/537.36',
        'referer': 'https://www.bilibili.com',
    }

    if ini_login_Link_Prising(type=1) is not None:
        data = ini_login_Link_Prising(type=1)
        BILI_SESSDATA: Optional[str] = f'{data["sessdata"]}'
    else:
        BILI_SESSDATA: Optional[str] = f' '
    # 构建哔哩哔哩的Credential
    credential = Credential(sessdata=BILI_SESSDATA)
    return BILIBILI_HEADER,credential,BILI_SESSDATA

def add_rounded_rectangle(draw, xy, radius, fill):
    """绘制圆角矩形"""
    x0, y0, x1, y1 = xy
    draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
    draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)
    draw.pieslice([x0, y0, x0 + 2 * radius, y0 + 2 * radius], 180, 270, fill=fill)
    draw.pieslice([x1 - 2 * radius, y0, x1, y0 + 2 * radius], 270, 360, fill=fill)
    draw.pieslice([x0, y1 - 2 * radius, x0 + 2 * radius, y1], 90, 180, fill=fill)
    draw.pieslice([x1 - 2 * radius, y1 - 2 * radius, x1, y1], 0, 90, fill=fill)

def draw_video_thumbnail():
    # 打开模板图片

    file_path = 'manshuo_data/'
    template_path=f'{file_path}check.png'
    output_path=f'{file_path}correct-copy.png'
    template = Image.open(template_path).convert("RGBA")
    draw = ImageDraw.Draw(template)

    resize_x=370
    resize_y=260
    resize_x_touxiang=90
    resize_y_touxiang=90

    hot_get_bili = sync(hot.get_hot_videos())
    number=0
    for context_check in hot_get_bili['list']:

        print(number)
        if number == 8:break
        text=context_check[f'title']
        thumbnail_path_url = context_check[f'pic']
        touxiang_path_url = context_check['owner']['face']
        thumbnail_path=f'{file_path}fengmian.png'
        touxiang_path=f'{file_path}touxiang.png'
        response = requests.get(thumbnail_path_url)
        with open(thumbnail_path, 'wb') as file:
            file.write(response.content)
        response = requests.get(touxiang_path_url)
        with open(touxiang_path, 'wb') as file:
            file.write(response.content)

        x_check=number%2
        y_check=number//2
        #print(x_check,y_check)
        paste_x=146+x_check*430
        paste_y=343+y_check*394
        paste_x_touxiang=paste_x
        paste_y_touxiang=paste_y+283

        thumbnail = Image.open(thumbnail_path).resize((resize_x, resize_y), Image.Resampling.LANCZOS)
        mask = Image.new("L", (resize_x, resize_y), 0)
        mask_draw = ImageDraw.Draw(mask)
        add_rounded_rectangle(mask_draw, (0, 0, resize_x, resize_y), radius=20, fill=255)
        template.paste(thumbnail, (paste_x, paste_y), mask)

        thumbnail = Image.open(touxiang_path).resize((resize_x_touxiang, resize_y_touxiang), Image.Resampling.LANCZOS)
        mask = Image.new("L", (resize_x_touxiang, resize_y_touxiang), 0)
        mask_draw = ImageDraw.Draw(mask)
        add_rounded_rectangle(mask_draw, (0, 0, resize_x_touxiang, resize_y_touxiang), radius=45, fill=255)
        template.paste(thumbnail, (paste_x_touxiang, paste_y_touxiang), mask)

        text = [text[i:i + 9] for i in range(0, len(text), 9)]
        text = text[:2]
        text = '\n'.join(text)
        # 添加文案
        font = ImageFont.truetype(f"{file_path}微软雅黑.ttf", 30)  # 替换为实际字体路径
        text_position = (paste_x_touxiang+100, paste_y_touxiang+5)  # 文案位置
        draw.text(text_position, text, font=font, fill="black")
        number += 1
    # 保存输出图片
    template.save(output_path)
    #template.show()

async def download_b_file(url, full_file_name, progress_callback):
    """
        下载视频文件和音频文件
    :param url:
    :param full_file_name:
    :param progress_callback:
    :return:
    """
    BILIBILI_HEADER = {
        'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 '
            'Safari/537.36',
        'referer': 'https://www.bilibili.com',
    }
    async with httpx.AsyncClient(transport=httpx.AsyncHTTPTransport(local_address="0.0.0.0")) as client:
        async with client.stream("GET", url, headers=BILIBILI_HEADER) as resp:
            current_len = 0
            total_len = int(resp.headers.get('content-length', 0))
            print(total_len)
            async with aiofiles.open(full_file_name, "wb") as f:
                async for chunk in resp.aiter_bytes():
                    current_len += len(chunk)
                    await f.write(chunk)
                    progress_callback(f'下载进度：{round(current_len / total_len, 3)}')

def download_and_process_image(image_url, save_path):
    """
    下载网络图片，获取中央正方形区域并保存
    """
    def crop_center_square(image):
        width, height = image.size
        min_edge = min(width, height)
        left = (width - min_edge) // 2
        top = (height - min_edge) // 2
        right = left + min_edge
        bottom = top + min_edge
        return image.crop((left, top, right, bottom))
    response = requests.get(image_url)
    if response.status_code == 200:
        image_data = BytesIO(response.content)
        image = Image.open(image_data)
        square_image = crop_center_square(image)
        square_image.save(save_path)

async def merge_file_to_mp4(v_full_file_name: str, a_full_file_name: str, output_file_name: str, log_output: bool = False):
    """
    合并视频文件和音频文件
    :param v_full_file_name: 视频文件路径
    :param a_full_file_name: 音频文件路径
    :param output_file_name: 输出文件路径
    :param log_output: 是否显示 ffmpeg 输出日志，默认忽略
    :return:
    """
    print(f'正在合并：{output_file_name}')

    # 构建 ffmpeg 命令
    command = f'ffmpeg -y -i "{v_full_file_name}" -i "{a_full_file_name}" -c copy "{output_file_name}"'
    stdout = None if log_output else subprocess.DEVNULL
    stderr = None if log_output else subprocess.DEVNULL

    if platform.system() == "Windows":
        # Windows 下使用 run_in_executor
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: subprocess.call(command, shell=True, stdout=stdout, stderr=stderr)
        )
    else:
        # 其他平台使用 create_subprocess_shell
        process = await asyncio.create_subprocess_shell(
            command,
            shell=True,
            stdout=stdout,
            stderr=stderr
        )
        await process.communicate()

def extra_bili_info(video_info):
    """
        格式化视频信息
    """
    video_state = video_info['stat']
    video_like, video_coin, video_favorite, video_share, video_view, video_danmaku, video_reply = video_state['like'], \
        video_state['coin'], video_state['favorite'], video_state['share'], video_state['view'], video_state['danmaku'], \
        video_state['reply']

    video_data_map = {
        "点赞": video_like,
        "硬币": video_coin,
        "收藏": video_favorite,
        "分享": video_share,
        "总播放量": video_view,
        "弹幕数量": video_danmaku,
        "评论": video_reply
    }

    video_info_result = ""
    for key, value in video_data_map.items():
        if int(value) > 10000:
            formatted_value = f"{value / 10000:.1f}万"
        else:
            formatted_value = value
        video_info_result += f"{key}: {formatted_value} | "

    return video_info_result

#B站将av号转化为bv号
def av_to_bv(av_link):
    # AV号和BV号转换核心算法
    def av_to_bv_core(av_number):
        table = 'fZodR9XQDSUm21yCkr6zBqFLu4caZJMe5nvg7w8ETpKHYx3WjhAtGNPV'
        tr = [11, 10, 3, 8, 4, 6]
        xor = 177451812
        add = 8728348608

        av_number = int(av_number)  # 转为整数
        av_number = (av_number ^ xor) + add
        bv = list("BV1  4 1 7  ")

        for i in range(6):
            bv[tr[i]] = table[av_number // 58**i % 58]

        return ''.join(bv)

    # 从链接中提取 AV 号
    match = re.search(r'av(\d+)', av_link)
    if match:
        av_number = match.group(1)  # 提取数字部分
        return av_to_bv_core(av_number)
    else:
        raise ValueError("输入链接中不包含有效的 AV 号")

