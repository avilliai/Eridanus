from bilibili_api import hot, sync
from bilibili_api import video, Credential, live, article
from bilibili_api.favorite_list import get_video_favorite_list_content
from bilibili_api import dynamic
from bilibili_api.opus import Opus
from bilibili_api.video import VideoDownloadURLDataDetecter
import os
import requests
import asyncio
import platform
import subprocess
import re
import aiofiles
import httpx
from urllib.parse import urlparse
from pydantic import BaseModel, Extra
from typing import Optional
import asyncio
import os.path
from functools import wraps
from typing import cast, Iterable, Union
from urllib.parse import parse_qs
from PIL import Image, ImageDraw, ImageFont, ImageOps,ImageFilter
import textwrap
from datetime import datetime, timedelta

#from draw import draw_adaptive_graphic_and_textual
from plugins.resource_search_plugin.Link_parsing.draw import draw_adaptive_graphic_and_textual

from io import BytesIO

BILIBILI_HEADER = {
    'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 '
        'Safari/537.36',
    'referer': 'https://www.bilibili.com',
}
BILI_SESSDATA: Optional[str] = ''

# 构建哔哩哔哩的Credential
credential = Credential(sessdata=BILI_SESSDATA)
GLOBAL_NICKNAME='枫与岚'
VIDEO_DURATION_MAXIMUM=10

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
    return output_path
    #template.show()

async def download_b_file(url, full_file_name, progress_callback):
    """
        下载视频文件和音频文件
    :param url:
    :param full_file_name:
    :param progress_callback:
    :return:
    """
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
        return full_file_name



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
    return save_path


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
async def bilibili(url,filepath=None,is_twice=None) :
    """
        哔哩哔哩解析
    :param bot:
    :param event:
    :return:
    """
    # 消息
    #url: str = str(event.message).strip()




    if not ( 'bili' in url or 'b23' in url ):return
    #构建绘图消息链
    if filepath is None: filepath = 'data/'
    contents=[]
    contents_dy=[]
    avatar_path=f'{filepath}touxiang.png'
    name=None
    Time=None
    orig_desc=None
    orig_cover=None
    type=None
    introduce=None
    desc=None
    #(contents,avatar_path,name,Time,type,introduce)=0
    # 正则匹配
    url_reg = r"(http:|https:)\/\/(space|www|live).bilibili.com\/[A-Za-z\d._?%&+\-=\/#]*"
    b_short_rex = r"(https?://(?:b23\.tv|bili2233\.cn)/[A-Za-z\d._?%&+\-=\/#]+)"
    # 处理短号、小程序问题
    if "b23.tv" in url or "bili2233.cn" in url or "QQ小程序" in url :
        b_short_url = re.search(b_short_rex, url.replace("\\", ""))[0]
        print(f'b_short_url:{b_short_url}')
        resp = httpx.get(b_short_url, headers=BILIBILI_HEADER, follow_redirects=True)
        url: str = str(resp.url)
        print(f'url:{url}')
    # AV/BV处理
    if"av" in url:url= 'https://www.bilibili.com/video/' + av_to_bv(url)
    if re.match(r'^BV[1-9a-zA-Z]{10}$', url):
        url = 'https://www.bilibili.com/video/' + url
    #print(f'BV_url:{url}')
    #print(BILI_SESSDATA)
    # ===============发现解析的是动态，转移一下===============
    if ('t.bilibili.com' in url or '/opus' in url) and BILI_SESSDATA != '':
        # 去除多余的参数
        if '?' in url:
            url = url[:url.index('?')]
        dynamic_id = int(re.search(r'[^/]+(?!.*/)', url)[0])
        dy = dynamic.Dynamic(dynamic_id, credential)
        is_opus = dy.is_opus()#判断动态是否为图文

        if is_opus is False:#若判断为图文则换另一种方法读取

            dynamic_info = await Opus(dynamic_id, credential).get_info()
            if dynamic_info is not None:
                title = dynamic_info['item']['basic']['title']
                paragraphs = []
                for module in dynamic_info['item']['modules']:
                    if 'module_content' in module:
                        paragraphs = module['module_content']['paragraphs']
                        break
                desc = paragraphs[0]['text']['nodes'][0]['word']['words']
                #获取头像以及名字
                for module in dynamic_info['item']['modules']:
                    if 'module_author' in module:
                        modules = module['module_author']
                        owner_cover,owner_name,pub_time = modules['face'],modules['name'],modules['pub_time']

                        response = requests.get(owner_cover)
                        with open(avatar_path, 'wb') as file:
                            file.write(response.content)
                        break
                contents.append(f"{desc}")

                tags=''
                for tags_check in paragraphs[0]['text']['nodes']:
                    if tags_check['type'] =='TEXT_NODE_TYPE_RICH':
                        tags+=tags_check['rich']['text'] + ' '
                contents.append(f'tag:{tags}')

                check_number=0
                #print(paragraphs)
                try:
                    pics_context=paragraphs[1]['pic']['pics']
                except IndexError:
                    pics_context=dynamic_info['item']['modules'][0]['module_top']['display']['album']['pics']
                for pics in pics_context:
                    pics_url = pics['url']
                    if len(pics_context) >= 2:
                        download_and_process_image(pics_url,f'{filepath}cover{check_number}.png')
                    else:
                        response = requests.get(pics_url)
                        with open(f'{filepath}cover{check_number}.png', 'wb') as file:
                            file.write(response.content)
                    contents.append(f'{filepath}cover{check_number}.png')
                    check_number+=1
                draw_adaptive_graphic_and_textual(contents, avatar_path=avatar_path, name=owner_name,
                                                  Time=f'{pub_time}',filepath=filepath)
                return contents,avatar_path,owner_name,pub_time,type,introduce
            #print(f"{GLOBAL_NICKNAME}识别：B站动态，{title}\n{desc}\n{pics}")

        if is_opus is True:
            dynamic_info = await dy.get_info()
            print(dynamic_info)
            orig_check=1#判断是否为转发，转发为2
            type_set=None
            if dynamic_info is not None:
                paragraphs = []
                for module in dynamic_info['item']:
                    if 'orig' in module:
                        orig_check=2
                        orig_context=dynamic_info['item'][module]
                for module in dynamic_info['item']['modules']:
                    if 'module_dynamic' in module:
                        if orig_check==1:
                            type_set=13
                        elif orig_check==2:
                            paragraphs = dynamic_info['item']['modules']['module_dynamic']
                            type_set=14
                        break
                #获取头像以及名字
                owner_cover=dynamic_info['item']['modules']['module_author']['face']
                owner_name=dynamic_info['item']['modules']['module_author']['name']
                pub_time=dynamic_info['item']['modules']['module_author']['pub_time']
                response = requests.get(owner_cover)
                with open(avatar_path, 'wb') as file:
                    file.write(response.content)
                if orig_check ==1:
                    if 'opus' in dynamic_info['item']['modules']['module_dynamic']['major']:
                        opus_paragraphs = dynamic_info['item']['modules']['module_dynamic']['major']['opus']
                        title = opus_paragraphs['summary']['text']
                        contents.append(title)
                    else:
                        paragraphs = dynamic_info['item']['modules']['module_dynamic']['major']['archive']
                        title,desc,cover,bvid=paragraphs['title'],paragraphs['desc'],paragraphs['cover'],paragraphs['bvid']
                        response = requests.get(cover)
                        with open(f'{filepath}cover.png', 'wb') as file:
                            file.write(response.content)
                        contents.append(f'{filepath}cover.png')
                        contents.append(title)
                    draw_adaptive_graphic_and_textual(contents, avatar_path=avatar_path, name=owner_name,
                                                          Time=f'{pub_time}', type=type_set, introduce=desc,
                                                      filepath=filepath)
                    return contents, avatar_path, owner_name, pub_time, type, desc
                elif orig_check ==2:
                    words=paragraphs['desc']['text']
                    #title=paragraphs['desc']['rich_text_nodes']
                    contents.append(words)

                    for module in orig_context['modules']:
                        if 'module_dynamic' in module:
                            if 'opus' in orig_context['modules']['module_dynamic']['major']:
                                opus_orig_paragraphs=orig_context['modules']['module_dynamic']['major']['opus']
                                orig_title=opus_orig_paragraphs['summary']['text']
                                contents_dy.append(orig_title)
                                print(opus_orig_paragraphs)
                                check_number = 0
                                pics_context = opus_orig_paragraphs['pics']
                                for pics in pics_context:
                                    pics_url = pics['url']
                                    if len(pics_context) >= 2:
                                        download_and_process_image(pics_url, f'{filepath}cover{check_number}.png')
                                    else:
                                        response = requests.get(pics_url)
                                        with open(f'{filepath}cover{check_number}.png', 'wb') as file:
                                            file.write(response.content)
                                    contents_dy.append(f'{filepath}cover{check_number}.png')
                                    check_number +=1
                            else:
                                orig_paragraphs = orig_context['modules']['module_dynamic']['major']['archive']
                                orig_title, orig_desc, orig_cover, orig_bvid = orig_paragraphs['title'], orig_paragraphs['desc'], orig_paragraphs['cover'], orig_paragraphs['bvid']
                                response = requests.get(orig_cover)
                                with open(f'{filepath}cover.png', 'wb') as file:
                                    file.write(response.content)
                                contents_dy.append(f'{filepath}cover.png')
                                contents_dy.append(orig_title)

                                check_number = 0
                                # print(paragraphs)
                                try:
                                    pics_context = paragraphs[1]['pic']['pics']
                                except KeyError:
                                    pics_context = []
                                for pics in pics_context:
                                    pics_url = pics['url']
                                    if len(pics_context) >= 2:
                                        download_and_process_image(pics_url, f'{filepath}cover{check_number}.png')
                                    else:
                                        response = requests.get(pics_url)
                                        with open(f'{filepath}cover{check_number}.png', 'wb') as file:
                                            file.write(response.content)
                                    contents_dy.append(f'{filepath}cover{check_number}.png')
                                    check_number += 1


                    orig_pub_time=orig_context['modules']['module_author']['pub_time']
                    orig_owner_name = orig_context['modules']['module_author']['name']
                    orig_owner_cover = orig_context['modules']['module_author']['face']





                    if is_twice is True:
                        response = requests.get(orig_owner_cover)
                        with open(avatar_path, 'wb') as file:
                            file.write(response.content)
                        if orig_pub_time == '':
                            return contents_dy, avatar_path, orig_owner_name, pub_time, type, orig_desc
                        else:
                            return contents_dy, avatar_path, orig_owner_name, orig_pub_time, type, orig_desc
                    orig_url= 'https://t.bilibili.com/' + orig_context['id_str']


                    orig_contents,orig_avatar_path,orig_name,orig_Time,orig_type,orig_introduce=await bilibili(url,f'{filepath}orig_',is_twice=True)
                    draw_adaptive_graphic_and_textual(contents, avatar_path=avatar_path,
                                                      name=owner_name, Time=f'{pub_time}', type=type_set,
                                                      introduce=orig_desc,filepath=filepath,
                                                      contents_dy=orig_contents, orig_avatar_path=orig_avatar_path,
                                                      orig_name=orig_name,orig_Time=orig_Time)




        return
    # 直播间识别
    if 'live' in url:
        # https://live.bilibili.com/30528999?hotRank=0
        room_id = re.search(r'\/(\d+)$', url).group(1)
        room = live.LiveRoom(room_display_id=int(room_id))
        data_get_url_context=await room.get_room_info()
        #print(data_get_url_context['room_info'])
        room_info = data_get_url_context['room_info']
        title, cover, keyframe = room_info['title'], room_info['cover'], room_info['keyframe']
        owner_name,owner_cover = data_get_url_context['anchor_info']['base_info']['uname'], data_get_url_context['anchor_info']['base_info']['face']
        #introduce=data_get_url_context['anchor_info']['base_info']['official_info']['title']
        area_name,parent_area_name=room_info['area_name'],room_info['parent_area_name']

        introduce=f'{parent_area_name} {area_name}'
        response = requests.get(owner_cover)
        with open(f'{filepath}touxiang.png', 'wb') as file:
            file.write(response.content)
        response = requests.get(cover)
        with open(f'{filepath}cover.png', 'wb') as file:
            file.write(response.content)
        contents.append(f'{filepath}cover.png')
        contents.append(f"{title}")

        if f'{room_info["live_status"]}' == '1':
            live_status, live_start_time = room_info['live_status'], room_info['live_start_time']
            video_time=live_start_time
            days = video_time // (24 * 3600)
            video_time %= (24 * 3600)
            hours = video_time // 3600
            video_time %= 3600
            minutes = video_time // 60
            video_time %= 60
            video_time = f'直播了 {days}天{hours}小时{minutes}分'
        else:video_time='暂未开启直播'


        print(room_info['online'])

        draw_adaptive_graphic_and_textual(contents, avatar_path=avatar_path, name=owner_name,
                                          Time=f'{video_time}',type=12,introduce=introduce,filepath=filepath)
        return contents, avatar_path, owner_name, video_time, type, introduce
    # 专栏识别
    if 'read' in url:
        return
    # 收藏夹识别
    if 'favlist' in url and BILI_SESSDATA != '':
        return
    # 获取视频信息
    video_id = re.search(r"video\/[^\?\/ ]+", url)[0].split('/')[1]
    print(video_id)
    v = video.Video(video_id, credential=credential)
    try:
        video_info = await v.get_info()
    except Exception as e:
        print('无法获取视频内容，该进程已退出')
    #print(video_info)

    owner_cover_url=video_info['owner']['face']
    owner_name = video_info['owner']['name']
    #print(owner_cover)
    if video_info is None:
        print(f"{GLOBAL_NICKNAME}识别：B站，出错，无法获取数据！")
        return
    video_title, video_cover, video_desc, video_duration = video_info['title'], video_info['pic'], video_info['desc'], \
        video_info['duration']
    video_time = datetime.utcfromtimestamp(video_info['pubdate']) + timedelta(hours=8)
    video_time=video_time.strftime('%Y-%m-%d %H:%M:%S')
    #print(video_title, video_cover, video_desc, video_duration)

    # 校准 分p 的情况
    page_num = 0
    if 'pages' in video_info:
        # 解析URL
        parsed_url = urlparse(url)
        # 检查是否有查询字符串
        if parsed_url.query:
            # 解析查询字符串中的参数
            query_params = parse_qs(parsed_url.query)
            # 获取指定参数的值，如果参数不存在，则返回None
            page_num = int(query_params.get('p', [1])[0]) - 1
        else:
            page_num = 0
        if 'duration' in video_info['pages'][page_num]:
            video_duration = video_info['pages'][page_num].get('duration', video_info.get('duration'))
        else:
            # 如果索引超出范围，使用 video_info['duration'] 或者其他默认值
            video_duration = video_info.get('duration', 0)
    # 删除特殊字符
    #print(video_title)
    #video_title = delete_boring_characters(video_title)
    # 截断下载时间比较长的视频
    online = await v.get_online()
    online_str = f'🏄‍♂️ 总共 {online["total"]} 人在观看，{online["count"]} 人在网页端观看'
    #print(f"\n{GLOBAL_NICKNAME}识别：B站，{video_title}\n{extra_bili_info(video_info)}\n📝 简介：{video_desc}\n{online_str}")

    response = requests.get(video_cover)
    with open(f'{filepath}cover.png', 'wb') as file:
        file.write(response.content)
    contents.append(f'{filepath}cover.png')

    response = requests.get(owner_cover_url)
    with open(avatar_path, 'wb') as file:
        file.write(response.content)

    contents.append(f"{video_title}")
    introduce=f'{video_desc}'
    type=11
    draw_adaptive_graphic_and_textual(contents, avatar_path=avatar_path, name=owner_name,Time=f'{video_time}',type=type,introduce=introduce,filepath=filepath)
    return contents, avatar_path, owner_name, video_time, type, introduce


#draw_video_thumbnail()
if __name__ == "__main__":
    url='https://t.bilibili.com/1018996014819835911'

    asyncio.run(bilibili(url))
