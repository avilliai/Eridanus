from bilibili_api import video, Credential, live, article
from bilibili_api import dynamic
from bilibili_api.opus import Opus
import os
import requests
import base64
import re
import httpx
from urllib.parse import urlparse
import asyncio
import os.path
from urllib.parse import parse_qs
from datetime import datetime, timedelta
import json

from developTools.utils.logger import get_logger
from plugins.resource_search_plugin.Link_parsing.core.draw import draw_adaptive_graphic_and_textual
from plugins.resource_search_plugin.Link_parsing.core.bili import bili_init,av_to_bv,download_and_process_image
from plugins.resource_search_plugin.Link_parsing.core.weibo import mid2id,WEIBO_SINGLE_INFO
from plugins.resource_search_plugin.Link_parsing.core.common import download_video,download_img,add_append_img
from plugins.resource_search_plugin.Link_parsing.core.tiktok import generate_x_bogus_url, dou_transfer_other, \
    COMMON_HEADER,DOUYIN_VIDEO,URL_TYPE_CODE_DICT,DY_TOUTIAO_INFO
from plugins.resource_search_plugin.Link_parsing.core.login_core import ini_login_Link_Prising
from plugins.resource_search_plugin.Link_parsing.core.acfun import parse_url, download_m3u8_videos, parse_m3u8, merge_ac_file_to_mp4
from plugins.resource_search_plugin.Link_parsing.core.xhs import XHS_REQ_LINK

import inspect
import aiohttp

filepath_init=f'{os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(bili_init))))}/data/cache/'
GLOBAL_NICKNAME='Bot'
if not os.path.exists(filepath_init):  # 初始化检测文件夹
        os.makedirs(filepath_init)
logger=get_logger()
async def bilibili(url,filepath=None,is_twice=None):
    """
        哔哩哔哩解析
    :param bot:
    :param event:
    :return:
    """
    # 消息
    #url: str = str(event.message).strip()

    BILIBILI_HEADER, credential,BILI_SESSDATA=bili_init()#获取构建credential
    #logger.info(f'credential: {credential}')

    if not ( 'bili' in url or 'b23' in url ):return
    #构建绘图消息链
    if filepath is None:
        filepath = filepath_init
        #logger.info(filepath_init)
    contents=[]
    contents_dy=[]
    #avatar_path=f'{filepath}touxiang.png'
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
        #logger.info(f'b_short_url:{b_short_url}')
        resp = httpx.get(b_short_url, headers=BILIBILI_HEADER, follow_redirects=True)
        url: str = str(resp.url)
        #logger.info(f'url:{url}')
    # AV/BV处理
    if"av" in url:url= 'https://www.bilibili.com/video/' + av_to_bv(url)
    if re.match(r'^BV[1-9a-zA-Z]{10}$', url):
        url = 'https://www.bilibili.com/video/' + url
    # ===============发现解析的是动态，转移一下===============
    if ('t.bilibili.com' in url or '/opus' in url or '/space' in url ) and BILI_SESSDATA != '':
        # 去除多余的参数
        if '?' in url:
            url = url[:url.index('?')]
        dynamic_id = int(re.search(r'[^/]+(?!.*/)', url)[0])
        #logger.info(dynamic_id)
        dy = dynamic.Dynamic(dynamic_id, credential)
        is_opus = dy.is_opus()#判断动态是否为图文

        if is_opus is False:#若判断为图文则换另一种方法读取
            #logger.info('not opus')
            dynamic_info = await Opus(dynamic_id, credential).get_info()
            tags = ''
            if dynamic_info is not None:
                title = dynamic_info['item']['basic']['title']
                paragraphs = []
                for module in dynamic_info['item']['modules']:
                    if 'module_content' in module:
                        paragraphs = module['module_content']['paragraphs']
                        break
                #logger.info(paragraphs)
                for desc_check in paragraphs[0]['text']['nodes']:
                    if 'word' in desc_check:
                        desc = desc_check['word']['words']
                        if f'{desc}' not in {'',' '}:
                            contents.append(f"{desc}")
                for tags_check in paragraphs[0]['text']['nodes']:
                    if tags_check['type'] =='TEXT_NODE_TYPE_RICH':
                        tags+=tags_check['rich']['text'] + ' '
                if tags != '':
                    contents.append(f'tag:{tags}')

                #获取头像以及名字
                for module in dynamic_info['item']['modules']:
                    if 'module_author' in module:
                        modules = module['module_author']
                        owner_cover,owner_name,pub_time = modules['face'],modules['name'],modules['pub_time']
                        avatar_path =(await asyncio.gather(*[asyncio.create_task(download_img(owner_cover, f'{filepath}'))]))[0]
                        break

                check_number=0
                try:
                    pics_context=paragraphs[1]['pic']['pics']
                except IndexError:
                    pics_context=dynamic_info['item']['modules'][0]['module_top']['display']['album']['pics']

                contents = await add_append_img(contents, await asyncio.gather(*[asyncio.create_task(download_img(item['url'], f'{filepath}', len=len(pics_context))) for item in pics_context]))
                #logger.info(contents)
                if is_twice is not True:
                    out_path=draw_adaptive_graphic_and_textual(contents, avatar_path=avatar_path, name=owner_name,
                                                  Time=f'{pub_time}',filepath=filepath,type_software='BiliBili 动态',
                                      color_software=(251,114,153,80),output_path_name=f'{dynamic_id}')
                    return out_path,f'https://t.bilibili.com/{dynamic_id}'
                return contents,avatar_path,owner_name,pub_time,type,introduce
            #logger.info(f"{GLOBAL_NICKNAME}识别：B站动态，{title}\n{desc}\n{pics}")

        if is_opus is True:
            dynamic_info = await dy.get_info()
            #logger.info(dynamic_info)
            #logger.info('is opus')
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
                avatar_path = (await asyncio.gather(*[asyncio.create_task(download_img(owner_cover, f'{filepath}'))]))[0]
                if orig_check ==1:
                    type_software='BiliBili 动态'
                    if 'opus' in dynamic_info['item']['modules']['module_dynamic']['major']:
                        opus_paragraphs = dynamic_info['item']['modules']['module_dynamic']['major']['opus']
                        title = opus_paragraphs['summary']['text']
                        contents.append(title)
                    elif 'live_rcmd' in dynamic_info['item']['modules']['module_dynamic']['major']:
                        live_paragraphs = dynamic_info['item']['modules']['module_dynamic']['major']['live_rcmd']
                        content = json.loads(live_paragraphs['content'])
                        title,cover,pub_time = content['live_play_info']['title'],content['live_play_info']['cover'],content['live_play_info']['live_start_time']
                        contents.append((await asyncio.gather(*[asyncio.create_task(download_img(cover, f'{filepath}'))]))[0])
                        contents.append(title)
                        pub_time = datetime.fromtimestamp(pub_time).astimezone().strftime("%Y-%m-%d %H:%M:%S")
                        type_software = 'BiliBili 直播'
                    else:
                        paragraphs = dynamic_info['item']['modules']['module_dynamic']['major']['archive']
                        title,desc,cover,bvid=paragraphs['title'],paragraphs['desc'],paragraphs['cover'],paragraphs['bvid']
                        contents.append((await asyncio.gather(*[asyncio.create_task(download_img(cover, f'{filepath}'))]))[0])
                        contents.append(title)

                    if is_twice is not True:
                        out_path=draw_adaptive_graphic_and_textual(contents, avatar_path=avatar_path, name=owner_name,
                                                          Time=f'{pub_time}', type=type_set, introduce=desc,
                                                      filepath=filepath,type_software=type_software,
                                      color_software=(251,114,153,80),output_path_name=f'{dynamic_id}')
                        return out_path,f'https://t.bilibili.com/{dynamic_id}'
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
                                #logger.info(opus_orig_paragraphs)
                                contents_dy = await add_append_img(contents_dy, await asyncio.gather(*[
                                    asyncio.create_task(download_img(item['url'], f'{filepath}', len=len(opus_orig_paragraphs['pics'])))
                                    for item in opus_orig_paragraphs['pics']]))
                            else:
                                orig_paragraphs = orig_context['modules']['module_dynamic']['major']['archive']
                                orig_title, orig_desc, orig_cover, orig_bvid = orig_paragraphs['title'], orig_paragraphs['desc'], orig_paragraphs['cover'], orig_paragraphs['bvid']
                                contents_dy.append((await asyncio.gather(*[asyncio.create_task(download_img(orig_cover, f'{filepath}'))]))[0])
                                contents_dy.append(orig_title)
                                try:
                                    pics_context = paragraphs[1]['pic']['pics']
                                except KeyError:
                                    pics_context = []
                                contents_dy = await add_append_img(contents_dy, await asyncio.gather(*[
                                    asyncio.create_task(download_img(item['url'], f'{filepath}', len=len(pics_context)))for item in pics_context]))

                    orig_pub_time=orig_context['modules']['module_author']['pub_time']
                    orig_owner_name = orig_context['modules']['module_author']['name']
                    orig_owner_cover = orig_context['modules']['module_author']['face']

                    if is_twice is True:
                        avatar_path =(await asyncio.gather(*[asyncio.create_task(download_img(orig_owner_cover, f'{filepath}'))]))[0]
                        if orig_pub_time == '':
                            return contents_dy, avatar_path, orig_owner_name, pub_time, type, orig_desc
                        else:
                            return contents_dy, avatar_path, orig_owner_name, orig_pub_time, type, orig_desc
                    orig_url= 'orig_url:'+'https://t.bilibili.com/' + orig_context['id_str']
                    #logger.info(orig_url)


                    orig_contents,orig_avatar_path,orig_name,orig_Time,orig_type,orig_introduce=await bilibili(orig_url,f'{filepath}orig_',is_twice=True)

                    out_path=draw_adaptive_graphic_and_textual(contents, avatar_path=avatar_path,
                                                    name=owner_name, Time=f'{pub_time}', type=type_set,
                                                    introduce=orig_desc,filepath=filepath,
                                                    contents_dy=orig_contents, orig_avatar_path=orig_avatar_path,
                                                    orig_name=orig_name,orig_Time=orig_Time,
                                                    type_software='BiliBili 动态',
                                                    color_software=(251, 114, 153, 80),
                                                    output_path_name=f'{dynamic_id}',
                                                    orig_type_software='转发动态'
                                                    )
                    return out_path,f'https://t.bilibili.com/{dynamic_id}'
        return None
    # 直播间识别
    if 'live' in url:
        # https://live.bilibili.com/30528999?hotRank=0
        room_id = re.search(r'\/(\d+)$', url).group(1)
        room = live.LiveRoom(room_display_id=int(room_id))
        data_get_url_context=await room.get_room_info()
        #logger.info(data_get_url_context['room_info'])
        room_info = data_get_url_context['room_info']
        title, cover, keyframe = room_info['title'], room_info['cover'], room_info['keyframe']
        owner_name,owner_cover = data_get_url_context['anchor_info']['base_info']['uname'], data_get_url_context['anchor_info']['base_info']['face']
        #introduce=data_get_url_context['anchor_info']['base_info']['official_info']['title']
        area_name,parent_area_name=room_info['area_name'],room_info['parent_area_name']

        introduce=f'{parent_area_name} {area_name}'
        avatar_path = (await asyncio.gather(*[asyncio.create_task(download_img(owner_cover, f'{filepath}'))]))[0]
        contents.append((await asyncio.gather(*[asyncio.create_task(download_img(cover, f'{filepath}'))]))[0])
        contents.append(f"{title}")

        if f'{room_info["live_status"]}' == '1':
            live_status, live_start_time = room_info['live_status'], room_info['live_start_time']
            video_time = datetime.fromtimestamp(live_start_time).astimezone().strftime("%Y-%m-%d %H:%M:%S")
        else:video_time='暂未开启直播'
        #logger.info(room_info['online'])
        if is_twice is not True:
            out_path=draw_adaptive_graphic_and_textual(contents, avatar_path=avatar_path, name=owner_name,
                                          Time=f'{video_time}',type=12,introduce=introduce,filepath=filepath,type_software='BiliBili 直播',
                                      color_software=(251,114,153,80),output_path_name=f'{room_id}')
            return out_path,f'https://live.bilibili.com/{room_id}'
        return contents, avatar_path, owner_name, video_time, type, introduce
    # 专栏识别
    if 'read' in url:
        return None
    # 收藏夹识别
    if 'favlist' in url and BILI_SESSDATA != '':
        return None
    # 获取视频信息
    video_id = re.search(r"video\/[^\?\/ ]+", url)[0].split('/')[1]
    #logger.info(video_id)
    v = video.Video(video_id, credential=credential)
    try:
        video_info = await v.get_info()
    except Exception as e:
        logger.info('无法获取视频内容，该进程已退出')

    #logger.info(video_info)

    owner_cover_url=video_info['owner']['face']
    owner_name = video_info['owner']['name']
    #logger.info(owner_cover)
    if video_info is None:
        logger.info(f"识别：B站，出错，无法获取数据！")
        return None
    video_title, video_cover, video_desc, video_duration = video_info['title'], video_info['pic'], video_info['desc'], \
        video_info['duration']
    video_time = datetime.utcfromtimestamp(video_info['pubdate']) + timedelta(hours=8)
    video_time=video_time.strftime('%Y-%m-%d %H:%M:%S')
    #logger.info(video_title, video_cover, video_desc, video_duration)

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
    #logger.info(video_title)
    #video_title = delete_boring_characters(video_title)
    # 截断下载时间比较长的视频
    online = await v.get_online()
    online_str = f'🏄‍♂️ 总共 {online["total"]} 人在观看，{online["count"]} 人在网页端观看'
    #logger.info(f"\n{GLOBAL_NICKNAME}识别：B站，{video_title}\n{extra_bili_info(video_info)}\n📝 简介：{video_desc}\n{online_str}")

    #video_cover_path = await asyncio.gather(*[asyncio.create_task(download_img(video_cover, f'{filepath}'))])
    contents.append((await asyncio.gather(*[asyncio.create_task(download_img(video_cover, f'{filepath}'))]))[0])
    avatar_path = (await asyncio.gather(*[asyncio.create_task(download_img(owner_cover_url, f'{filepath}'))]))[0]

    contents.append(f"{video_title}")
    introduce=f'{video_desc}'
    type=11
    if is_twice is not True:
        out_path=draw_adaptive_graphic_and_textual(contents, avatar_path=avatar_path, name=owner_name,Time=f'{video_time}',type=type,introduce=introduce,
                                    filepath=filepath,type_software='BiliBili',
                                    color_software=(251,114,153,80),output_path_name=f'{video_id}')
        return out_path,url
    return contents, avatar_path, owner_name, video_time, type, introduce

async def dy(url,filepath=None):
    """
        抖音解析
    :param bot:
    :param event:
    :return:
    """
    if filepath is None:filepath = filepath_init
    contents=[]
    # 消息
    msg=url
    #logger.info(msg)
    # 正则匹配
    reg = r"(http:|https:)\/\/v.douyin.com\/[A-Za-z\d._?%&+\-=#]*"
    dou_url = re.search(reg, msg, re.I)[0]
    dou_url_2 = httpx.get(dou_url).headers.get('location')
    logger.info(f'dou_url:{dou_url}')
    #logger.info(f'dou_url_2:{dou_url_2}')

    # 实况图集临时解决方案，eg.  https://v.douyin.com/iDsVgJKL/
    if "share/slides" in dou_url_2:
        cover, author, title, images = await dou_transfer_other(dou_url)
        # 如果第一个不为None 大概率是成功
        if author is not None:
            logger.info(f"{GLOBAL_NICKNAME}识别：【抖音】\n作者：{author}\n标题：{title}")
            logger.info(url for url in images)
        # 截断后续操作
        return
    # logger.error(dou_url_2)
    reg2 = r".*(video|note)\/(\d+)\/(.*?)"
    # 获取到ID
    dou_id = re.search(reg2, dou_url_2, re.I)[2]
    # logger.info(dou_id)
    # 如果没有设置dy的ck就结束，因为获取不到
    douyin_ck=ini_login_Link_Prising(type=2)
    #logger.info(f'douyin_ck: {douyin_ck}')
    if douyin_ck is None:
        logger.info("无法获取到管理员设置的抖音ck！")
        #await douyin.send(Message(f"{GLOBAL_NICKNAME}识别：抖音，无法获取到管理员设置的抖音ck！"))
        return
    # API、一些后续要用到的参数
    headers = {
                  'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                  'referer': f'https://www.douyin.com/video/{dou_id}',
                  'cookie': douyin_ck
              } | COMMON_HEADER
    api_url = DOUYIN_VIDEO.replace("{}", dou_id)
    #logger.info(f'api_url: {api_url}')
    api_url = generate_x_bogus_url(api_url, headers)  # 如果请求失败直接返回
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url, headers=headers, timeout=10) as response:
            detail = await response.json()
            if detail is None:
                logger.info(f"{GLOBAL_NICKNAME}识别：抖音，解析失败！")
                #await douyin.send(Message(f"{GLOBAL_NICKNAME}识别：抖音，解析失败！"))
                return
            # 获取信息
            detail = detail['aweme_detail']
            formatted_json = json.dumps(detail, indent=4)
            #logger.info(formatted_json)
            # 判断是图片还是视频
            url_type_code = detail['aweme_type']
            url_type = URL_TYPE_CODE_DICT.get(url_type_code, 'video')
            #logger.info(f"{GLOBAL_NICKNAME}识别：抖音，{detail.get('desc')}")
            # 根据类型进行发送
            avatar_url,cover_url=detail['author']['avatar_thumb']['url_list'][0],detail['author']['cover_url'][0]['url_list'][1]
            owner_name=detail['author']['nickname']
            #logger.info(f'avatar_url: {avatar_url}\ncover_url: {cover_url}')
            download_img_funcs = [asyncio.create_task(download_img(avatar_url, f'{filepath}'))]
            avatar_path = await asyncio.gather(*download_img_funcs)
            video_time = datetime.utcfromtimestamp(detail['create_time']) + timedelta(hours=8)
            video_time = video_time.strftime('%Y-%m-%d %H:%M:%S')

            if url_type == 'video':
                # 识别播放地址
                player_uri = detail.get("video").get("play_addr")['uri']
                player_real_addr = DY_TOUTIAO_INFO.replace("{}", player_uri)
                cover_url = detail.get("video").get("dynamic_cover")['url_list'][0]
                #logger.info(f'cover_url: {cover_url}\nplayer_real_addr: {player_real_addr}')
                download_img_funcs = [asyncio.create_task(download_img(cover_url, f'{filepath}'))]
                cover_path = await asyncio.gather(*download_img_funcs)
                #logger.info(cover_path)
                contents = await add_append_img(contents, cover_path)
                context = detail.get("desc").replace('#', '\n#', 1)
                contents.append(f'{context}')

            elif url_type == 'image':
                # 无水印图片列表/No watermark image list
                no_watermark_image_list = []
                for i in detail['images']:
                    no_watermark_image_list.append(i['url_list'][0])
                #logger.info(no_watermark_image_list)
                download_img_funcs = [asyncio.create_task(download_img(item, f'{filepath}',len=len(no_watermark_image_list)))for item in no_watermark_image_list]
                links_path = await asyncio.gather(*download_img_funcs)
                contents = await add_append_img(contents, links_path)

                #await send_forward_both(bot, event, make_node_segment(bot.self_id, no_watermark_image_list))
                context = detail.get("desc").replace('#', '\n#', 1)
                contents.append(f'{context}')
            out_path = draw_adaptive_graphic_and_textual(contents, avatar_path=avatar_path[0], name=owner_name,
                                                         Time=f'{video_time}', type=11,
                                                         filepath=filepath, type_software='抖音',
                                                         color_software=(0, 0, 0, 80),
                                                         output_path_name=f'{dou_id}')
            return out_path, dou_url

async def wb(url,filepath=None):
    message = url
    weibo_id = None
    content=[]
    reg = r'(jumpUrl|qqdocurl)": ?"(.*?)"'
    if filepath is None: filepath = filepath_init
    # 处理卡片问题
    if 'com.tencent.structmsg' or 'com.tencent.miniapp' in message:
        match = re.search(reg, message)
        logger.info(match)
        if match:
            get_url = match.group(2)
            logger.info(get_url)
            if get_url:
                message = json.loads('"' + get_url + '"')
    else:
        message = message
    # logger.info(message)
    # 判断是否包含 "m.weibo.cn"
    if "m.weibo.cn" in message:
        # https://m.weibo.cn/detail/4976424138313924
        match = re.search(r'(?<=detail/)[A-Za-z\d]+', message) or re.search(r'(?<=m.weibo.cn/)[A-Za-z\d]+/[A-Za-z\d]+',
                                                                            message)
        weibo_id = match.group(0) if match else None

    # 判断是否包含 "weibo.com/tv/show" 且包含 "mid="
    elif "weibo.com/tv/show" in message and "mid=" in message:
        # https://weibo.com/tv/show/1034:5007449447661594?mid=5007452630158934
        match = re.search(r'(?<=mid=)[A-Za-z\d]+', message)
        if match:
            weibo_id = mid2id(match.group(0))

    # 判断是否包含 "weibo.com"
    elif "weibo.com" in message:
        # https://weibo.com/1707895270/5006106478773472
        match = re.search(r'(?<=weibo.com/)[A-Za-z\d]+/[A-Za-z\d]+', message)
        weibo_id = match.group(0) if match else None

    # 无法获取到id则返回失败信息
    if not weibo_id:
        logger.info("解析失败：无法获取到wb的id")
        #await weibo.finish(Message("解析失败：无法获取到wb的id"))
    # 最终获取到的 id
    weibo_id = weibo_id.split("/")[1] if "/" in weibo_id else weibo_id
    # 请求数据
    resp = httpx.get(WEIBO_SINGLE_INFO.replace('{}', weibo_id), headers={
                                                                            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                                                                            "cookie": "_T_WM=40835919903; WEIBOCN_FROM=1110006030; MLOGIN=0; XSRF-TOKEN=4399c8",
                                                                            "Referer": f"https://m.weibo.cn/detail/{id}",
                                                                        } | COMMON_HEADER).json()
    weibo_data = resp['data']
    formatted_json = json.dumps(weibo_data, indent=4)
    #logger.info(formatted_json)
    text, status_title, source, region_name, pics, page_info = (weibo_data.get(key, None) for key in
                                                                ['text', 'status_title', 'source', 'region_name',
                                                                 'pics', 'page_info'])
    owner_name,avatar_hd,video_time=weibo_data['user']['screen_name'],weibo_data['user']['avatar_hd'],weibo_data['created_at']
    download_img_funcs = [asyncio.create_task(download_img(avatar_hd, f'{filepath}',
                          headers={"Referer": "http://blog.sina.com.cn/"} | COMMON_HEADER))]
    avatar_path = await asyncio.gather(*download_img_funcs)
    # 发送消息
    #logger.info(f"{GLOBAL_NICKNAME}识别：微博，{re.sub(r'<[^>]+>', '', text)}\n{status_title}\n{source}\t{region_name if region_name else ''}")
    #logger.info(f'source:{source}\nregion_name:{region_name}')
    content.append(re.sub(r'<[^>]+>', '', text))

    if pics:
        formatted_json = json.dumps(pics, indent=4)
        #logger.info(formatted_json)
        pics = map(lambda x: x['url'], pics)
        length=0
        img_check=[]
        for context in pics:
            length+=1
            img_check.append(context)
        download_img_funcs = [asyncio.create_task(download_img(f'{item}', f'{filepath}', len=length)) for item in img_check]
        links_path = await asyncio.gather(*download_img_funcs)
        content=await add_append_img(content,links_path)
        # 清除图片
        for temp in links_path:
            pass
            #os.unlink(temp)
    if page_info:
        logger.info(page_info)
        formatted_json = json.dumps(page_info, indent=4)
        logger.info(formatted_json)
        if 'page_pic' in page_info:
            if page_info.get('type') != 'topic':
                page_pic=page_info.get('page_pic').get('url')
                #logger.info(page_pic)
                download_img_funcs = [asyncio.create_task(download_img(page_pic, f'{filepath}',headers={ "Referer": "http://blog.sina.com.cn/"} | COMMON_HEADER))]
                page_pic_path = await asyncio.gather(*download_img_funcs)
                content.append(page_pic_path[0])

    out_path = draw_adaptive_graphic_and_textual(content, avatar_path=avatar_path[0], name=owner_name,
                                                 Time=f'{video_time}', type=11,
                                                 filepath=filepath, type_software='微博',
                                                 color_software=(255, 92, 0, 80),
                                                 output_path_name=f'{weibo_id}')
    return out_path, None





async def xiaohongshu(url,filepath=None):
    """
        小红书解析
    :param event:
    :return:
    """
    contents=[]
    if filepath is None: filepath = filepath_init
    introduce=None
    msg_url = re.search(r"(http:|https:)\/\/(xhslink|(www\.)xiaohongshu).com\/[A-Za-z\d._?%&+\-=\/#@]*",
                        str(url).replace("&amp;", "&").strip())[0]
    # 如果没有设置xhs的ck就结束，因为获取不到
    xhs_ck = 'abRequestId=e3d4ef61-f346-535a-a112-68b10d9efc6c; webBuild=4.55.0; xsecappid=xhs-pc-web; a1=194774a388746xcxbkvy1cpolet8tpl1aowgnabuj50000141451; webId=4dc656746c488593fd6934c8d3aa5a41; acw_tc=0a0bb1cf17371681462132387eb7c2147a7b205c932cf35dedf7fa19210da0; websectiga=2a3d3ea002e7d92b5c9743590ebd24010cf3710ff3af8029153751e41a6af4a3; sec_poison_id=8fe8d55d-f891-4ad9-abfb-6bdae6c8ed1b; gid=yj4WW402KS0qyj4WW40qYl0DYW4KCSCDThvyE7VSUl1d9k28Y9U1yI888y4y42y8ij2SdJSy; web_session=040069b082fe7512875e235dbe354b75641d5e; unread={%22ub%22:%22678675cd000000000900db78%22%2C%22ue%22:%22678529ec000000002002a75f%22%2C%22uc%22:29}'
    xhs_ck=ini_login_Link_Prising(type=3)
    if xhs_ck == "":
        #logger.error(global_config)
        logger.info('小红书ck未能成功获取，已经推出')
        #await xhs.send(Message(f"{GLOBAL_NICKNAME}识别内容来自：【小红书】\n无法获取到管理员设置的小红书ck！"))
        return
    # 请求头
    headers = {
                  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
                            'application/signed-exchange;v=b3;q=0.9',
                  'cookie': xhs_ck,
              } | COMMON_HEADER
    if "xhslink" in msg_url:
        msg_url = httpx.get(msg_url, headers=headers, follow_redirects=True).url
        msg_url = str(msg_url)
    xhs_id = re.search(r'/explore/(\w+)', msg_url)
    if not xhs_id:
        xhs_id = re.search(r'/discovery/item/(\w+)', msg_url)
    if not xhs_id:
        xhs_id = re.search(r'source=note&noteId=(\w+)', msg_url)
    xhs_id = xhs_id[1]
    # 解析 URL 参数
    parsed_url = urlparse(msg_url)
    params = parse_qs(parsed_url.query)
    # 提取 xsec_source 和 xsec_token
    xsec_source = params.get('xsec_source', [None])[0] or "pc_feed"
    xsec_token = params.get('xsec_token', [None])[0]

    html = httpx.get(f'{XHS_REQ_LINK}{xhs_id}?xsec_source={xsec_source}&xsec_token={xsec_token}', headers=headers).text
    # response_json = re.findall('window.__INITIAL_STATE__=(.*?)</script>', html)[0]
    try:
        response_json = re.findall('window.__INITIAL_STATE__=(.*?)</script>', html)[0]
    except IndexError:
        logger.info(f"{GLOBAL_NICKNAME}识别内容来自：【小红书】\n当前ck已失效，请联系管理员重新设置的小红书ck！")
        #await xhs.send(Message(f"{GLOBAL_NICKNAME}识别内容来自：【小红书】\n当前ck已失效，请联系管理员重新设置的小红书ck！"))
        return
    response_json = response_json.replace("undefined", "null")
    response_json = json.loads(response_json)
    note_data = response_json['note']['noteDetailMap'][xhs_id]['note']
    formatted_json = json.dumps(note_data, indent=4)
    #logger.info(formatted_json)
    note_title,note_desc,type = note_data['title'],note_data['desc'], note_data['type']
    avatar_path = (await asyncio.gather(*[asyncio.create_task(download_img(note_data['user']['avatar'], f'{filepath}'))]))[0]
    if 'time' in note_data:
        xhs_time=note_data['time']
    elif 'lastUpdateTime' in note_data:
        xhs_time = note_data['lastUpdateTime']
    #logger.info(xhs_time)
    video_time = datetime.utcfromtimestamp(int(xhs_time)/1000) + timedelta(hours=8)
    video_time = video_time.strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f"{GLOBAL_NICKNAME}识别：小红书，{note_title}\n{note_desc}")
    if type == 'normal':
        #logger.info('这是一条解析有文字链接的图文:')
        image_list = note_data['imageList']
        for context in image_list:
            logger.info(context["urlDefault"])
        # 批量下载
        contents.append(f'{note_title}\n{note_desc}')
        contents = await add_append_img(contents, await asyncio.gather(
            *[asyncio.create_task(download_img(item['urlDefault'], f'{filepath}', len=len(image_list))) for item in
              image_list]))
    elif type == 'video':
        # 这是一条解析有水印的视频
        introduce=note_desc
        #logger.info(note_data['video'])
        video_url = note_data['video']['media']['stream']['h264'][0]['masterUrl']
        image_list = note_data['imageList']
        contents = await add_append_img(contents, await asyncio.gather(
            *[asyncio.create_task(download_img(item['urlDefault'], f'{filepath}', len=len(image_list))) for item in
              image_list]))
        contents.append(f'{note_title}')
        # ⚠️ 废弃，解析无水印视频video.consumer.originVideoKey
        # video_url = f"http://sns-video-bd.xhscdn.com/{note_data['video']['consumer']['originVideoKey']}"
        #path = await download_video(video_url)
        # await xhs.send(Message(MessageSegment.video(path)))
        #logger.info(path)
        #await auto_video_send(event, path)

    out_path = draw_adaptive_graphic_and_textual(contents, avatar_path=avatar_path, name=note_data['user']['nickname'],
                                                 Time=f'{video_time}', type=11,introduce=introduce,
                                                 filepath=filepath, type_software='小红书',
                                                 color_software=(255, 38, 66, 80),
                                                 output_path_name=f'{xhs_id}')


    # 发送图片
    # 清除图片
    for temp in contents:
        pass
        #os.unlink(temp)
    return out_path,None


async def link_prising(url,filepath=None):
    dy_path=None
    logger.info(url)
    if 'bili' in url or 'b23' in url:
        dy_path,url=await bilibili(url,filepath=filepath)
    elif 'douyin' in url or 'douyin' in url:
        dy_path,url=await dy(url, filepath=filepath)
    elif 'weibo' in url:
        dy_path,url=await wb(url, filepath=filepath)
    elif 'xhslink' in url or 'xiaohongshu' in url:
        dy_path,url=await xiaohongshu(url, filepath=filepath)
    return dy_path,url


#draw_video_thumbnail()
if __name__ == "__main__":#测试用，不用管
    #asyncio.run(dy(url))
    #asyncio.run(bilibili(url))
    #asyncio.run(wb(url))
    url='90 双木扶苏发布了一篇小红书笔记，快来看吧！ 😆 qfWhccRIsgcrjZj 😆 http://xhslink.com/a/DcAsetCH0703，复制本条信息，打开【小红书】App查看精彩内容！'
    url='90 双木扶苏发布了一篇小红书笔记，快来看吧！ 😆 qfWhccRIsgcrjZj 😆 http://xhslink.com/a/DcAsetCH0703，复制本条信息，打开【小红书】App查看精彩内容！'

    url='44 【来抄作业✨早秋彩色衬衫叠穿｜时髦知识分子风 - 杨意子_ | 小红书 - 你的生活指南】 😆 Inw56apL6vWYuoS 😆 https://www.xiaohongshu.com/discovery/item/64c0e9c0000000001201a7de?source=webshare&xhsshare=pc_web&xsec_token=AB8GfF7dOtdlB0n_mqoz61fDayAXpCqWbAz9xb45p6huE=&xsec_source=pc_share'
    url='79 【感谢大数据！椰青茉莉也太太太好喝了吧 - 胖琪琪 | 小红书 - 你的生活指南】 😆 78VORl9ln3YDBKi 😆 https://www.xiaohongshu.com/discovery/item/63dcee03000000001d022015?source=webshare&xhsshare=pc_web&xsec_token=ABJoHbAtOG98_7RnFR3Mf2MuQ1JC8tRVlzHPAG5BGKdCc=&xsec_source=pc_share'
    asyncio.run(xiaohongshu(url))

