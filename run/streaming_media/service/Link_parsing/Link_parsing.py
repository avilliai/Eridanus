import sys
import asyncio
import copy
from bilibili_api import video, live, article
from bilibili_api import dynamic
from bilibili_api.opus import Opus
from bilibili_api.video import VideoDownloadURLDataDetecter
import re
import httpx
from urllib.parse import urlparse
import time
import os.path
from urllib.parse import parse_qs
from datetime import datetime, timedelta
import json
import traceback
from developTools.utils.logger import get_logger
from run.streaming_media.service.Link_parsing.core.draw import draw_adaptive_graphic_and_textual
from run.streaming_media.service.Link_parsing.core.bili import bili_init,av_to_bv,download_b,info_search_bili
from run.streaming_media.service.Link_parsing.core.weibo import mid2id,WEIBO_SINGLE_INFO
from run.streaming_media.service.Link_parsing.core.common import download_video,download_img,add_append_img,GENERAL_REQ_LINK,get_file_size_mb
from run.streaming_media.service.Link_parsing.core.tiktok import generate_x_bogus_url, dou_transfer_other, \
    COMMON_HEADER,DOUYIN_VIDEO,URL_TYPE_CODE_DICT,DY_TOUTIAO_INFO
from run.streaming_media.service.Link_parsing.core.login_core import ini_login_Link_Prising
from run.streaming_media.service.Link_parsing.core.xhs import XHS_REQ_LINK
from run.streaming_media.service.Link_parsing.core.bangumi_core import claendar_bangumi_get_json,bangumi_subject_post_json,bangumi_subjects_get_json_PIL
import inspect
from asyncio import sleep
try:
    from bilibili_api import select_client
    select_client("httpx")
except ImportError:
    #旧版本兼容问题，整合包更新后删除此部分代码
    pass
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


import random
import os
from bs4 import BeautifulSoup


json_init={'status':False,'content':{},'reason':{},'pic_path':{},'url':{},'video_url':False,'soft_type':False}
filepath_init=f'{os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(bili_init))))}/data/cache/'
GLOBAL_NICKNAME='Bot'
if not os.path.exists(filepath_init):  # 初始化检测文件夹
    os.makedirs(filepath_init)
from run.resource_collector.service.engine_search import html_read
logger=get_logger()

name_qq_list={'漫朔':1270858640,'枫与岚':2319804644,'Lemony':2424378897,'forandsix':1004704649,'魏咸哲':1431631009}
card_url_list=['https://gal.manshuo.ink/usr/uploads/galgame/img/zhenhong.png',
               'https://gal.manshuo.ink/usr/uploads/galgame/img/suki.png',
               'https://gal.manshuo.ink/usr/uploads/galgame/img/sega.png',
               'https://gal.manshuo.ink/usr/uploads/galgame/img/teto.png',
               'https://gal.manshuo.ink/usr/uploads/galgame/img/tianli.png',
               'https://gal.manshuo.ink/usr/uploads/galgame/img/keai.png',
               'https://gal.manshuo.ink/usr/uploads/galgame/img/keai2.png',
               'https://gal.manshuo.ink/usr/uploads/galgame/img/miku.png',
               'https://gal.manshuo.ink/usr/uploads/galgame/img/milk.png',
               'https://gal.manshuo.ink/usr/uploads/galgame/img/xiaoqizou.png',
               'https://gal.manshuo.ink/usr/uploads/galgame/img/maimai.png',
               'https://gal.manshuo.ink/usr/uploads/galgame/img/mimi2.png',
               'https://gal.manshuo.ink/usr/uploads/galgame/img/mimi.png',
               'https://gal.manshuo.ink/usr/uploads/galgame/img/hyro1.png',
               'https://gal.manshuo.ink/usr/uploads/galgame/img/salt1.png',
               'https://gal.manshuo.ink/usr/uploads/galgame/img/zhenhong2.png',
               'https://gal.manshuo.ink/usr/uploads/galgame/img/guangguang.png',
               ]

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
    json_check = copy.deepcopy(json_init)
    json_check['soft_type'] = 'bilibili'
    json_check['status'] = True
    json_check['video_url'] = False
    #logger.info(f'credential: {credential}')
    if not ( 'bili' in url or 'b23' in url ):return
    #构建绘图消息链
    if filepath is None:
        filepath = filepath_init
    contents=[]
    contents_dy=[]
    emoji_list = []
    orig_desc=None
    type=None
    introduce=None
    desc=None
    avatar_json=None
    url_reg = r"(http:|https:)\/\/(space|www|live).bilibili.com\/[A-Za-z\d._?%&+\-=\/#]*"
    b_short_rex = r"(https?://(?:b23\.tv|bili2233\.cn)/[A-Za-z\d._?%&+\-=\/#]+)"
    # 处理短号、小程序问题
    if "b23.tv" in url or "bili2233.cn" in url or "QQ小程序" in url :
        b_short_url = re.search(b_short_rex, url.replace("\\", ""))[0]
        #logger.info(f'b_short_url:{b_short_url}')
        resp = httpx.get(b_short_url, headers=BILIBILI_HEADER, follow_redirects=True)
        url: str = str(resp.url)
        #print(f'url:{url}')
    # AV/BV处理
    if "av" in url:url= 'https://www.bilibili.com/video/' + av_to_bv(url)
    if re.match(r'^BV[1-9a-zA-Z]{10}$', url):
        url = 'https://www.bilibili.com/video/' + url
    json_check['url'] = url
    # ===============发现解析的是动态，转移一下===============
    if ('t.bilibili.com' in url or '/opus' in url or '/space' in url ) and BILI_SESSDATA != '':
        # 去除多余的参数
        if '?' in url:
            url = url[:url.index('?')]
        dynamic_id = int(re.search(r'[^/]+(?!.*/)', url)[0])
        #logger.info(dynamic_id)
        dy = dynamic.Dynamic(dynamic_id, credential)
        is_opus =await dy.is_opus()#判断动态是否为图文
        json_check['url'] = f'https://t.bilibili.com/{dynamic_id}'
        #is_opus=True
        try:
            if is_opus is False:#若判断为图文则换另一种方法读取
                logger.info('not opus')
                #print(dynamic_id)

                dynamic_info = await Opus(dynamic_id).get_info()
                avatar_json = await info_search_bili(dynamic_info, is_opus,filepath=filepath,card_url_list=card_url_list)

                tags = ''
                number=0
                text_list_check=''
                if dynamic_info is not None:
                    title = dynamic_info['item']['basic']['title']
                    paragraphs = []
                    for module in dynamic_info['item']['modules']:
                        if 'module_content' in module:
                            paragraphs = module['module_content']['paragraphs']
                            break
                    #print(json.dumps(paragraphs, indent=4))
                    for desc_check in paragraphs[0]['text']['nodes']:
                        if 'word' in desc_check:
                            desc = desc_check['word']['words']
                            if f'{desc}' not in {'',' '}:
                                text_list_check+=f"{desc}"
                        elif desc_check['type'] =='TEXT_NODE_TYPE_RICH':
                            if desc_check['rich']['type'] =='RICH_TEXT_NODE_TYPE_EMOJI':
                                emoji_list.append(desc_check['rich']['emoji']['icon_url'])
                                text_list_check += f'![{number}'
                                number += 1
                            else:
                                tags+=desc_check['rich']['text'] + ' '
                    if text_list_check != '':
                        contents.append(text_list_check)
                    if tags != '':
                        contents.append(f'tag:{tags}')

                    #获取头像以及名字
                    for module in dynamic_info['item']['modules']:
                        if 'module_author' in module:
                            modules = module['module_author']
                            owner_cover,owner_name,pub_time = modules['face'],modules['name'],modules['pub_time']
                            avatar_path =(await asyncio.gather(*[asyncio.create_task(download_img(owner_cover, f'{filepath}'))]))[0]
                            break
                    try:
                        pics_context=paragraphs[1]['pic']['pics']
                    except :
                        pics_context=dynamic_info['item']['modules'][0]['module_top']['display']['album']['pics']

                    contents = await add_append_img(contents, await asyncio.gather(*[asyncio.create_task(download_img(item['url'], f'{filepath}', len=len(pics_context))) for item in pics_context]))
                    if is_twice is not True:
                        out_path=draw_adaptive_graphic_and_textual(contents, avatar_path=avatar_path, name=owner_name,
                                                      Time=f'{pub_time}',filepath=filepath,type_software='BiliBili 动态',emoji_list=emoji_list,
                                          color_software=(251,114,153,80),output_path_name=f'{dynamic_id}',avatar_json=avatar_json)
                        json_check['pic_path'] = out_path
                        json_check['time'] = pub_time
                        return json_check
                    return contents,avatar_path,owner_name,pub_time,type,introduce,emoji_list
        except Exception as e:
            logger.error(f"{e}, 尝试使用其他方式解析")
            is_opus=True


        if is_opus is True:
            dynamic_info = await dy.get_info()
            logger.info('is opus')
            #print(json.dumps(dynamic_info, indent=4))
            orig_check=1        #判断是否为转发，转发为2
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
                    avatar_json = await info_search_bili(dynamic_info, is_opus, filepath=filepath,card_url_list=card_url_list)
                    #print('非转发')
                    type_software='BiliBili 动态'
                    if 'opus' in dynamic_info['item']['modules']['module_dynamic']['major']:
                        opus_paragraphs = dynamic_info['item']['modules']['module_dynamic']['major']['opus']
                        text_list_check = ''
                        number=0
                        pics_context=[]
                        print(json.dumps(opus_paragraphs, indent=4))


                        for text_check in opus_paragraphs['summary']['rich_text_nodes']:
                            #print('\n\n')
                            if 'emoji' in text_check:
                                #print(text_check['emoji']['icon_url'])
                                text_list_check += f'![{number}'
                                number += 1
                                emoji_list.append(text_check['emoji']['icon_url'])
                            elif 'orig_text' in text_check:
                                text_list_check += text_check['orig_text']
                        #print(text_list_check)
                        if dynamic_info['item']['type'] == 'DYNAMIC_TYPE_ARTICLE':
                            type_software = 'BiliBili 专栏'
                            contents.append(f"title:{opus_paragraphs['title']}")
                            contents.append(text_list_check)
                            for pic_check in opus_paragraphs['pics']:
                                pics_context.append(pic_check['url'])
                            contents = await add_append_img(contents, await asyncio.gather(*[asyncio.create_task(download_img(item, f'{filepath}', len=len(pics_context))) for item in pics_context]))
                        else:
                            contents.append(text_list_check)
                            for pic_check in opus_paragraphs['pics']:
                                pics_context.append(pic_check['url'])
                            contents = await add_append_img(contents, await asyncio.gather(*[asyncio.create_task(download_img(item, f'{filepath}', len=len(pics_context))) for item in pics_context]))
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
                                                      filepath=filepath,type_software=type_software,emoji_list=emoji_list,
                                      color_software=(251,114,153,80),output_path_name=f'{dynamic_id}',avatar_json=avatar_json)
                        json_check['pic_path'] = out_path
                        json_check['time'] = pub_time
                        return json_check
                    return contents, avatar_path, owner_name, pub_time, type, desc,emoji_list
                elif orig_check ==2:
                    #print(json.dumps(paragraphs, indent=4))

                    text_list_check = ''
                    number = 0
                    for text_check in paragraphs['desc']['rich_text_nodes']:
                        if 'emoji' in text_check:
                            # print(text_check['emoji']['icon_url'])
                            text_list_check += f'![{number}'
                            number += 1
                            emoji_list.append(text_check['emoji']['icon_url'])
                        elif 'orig_text' in text_check:
                            text_list_check += text_check['orig_text']
                    contents.append(text_list_check)
                    #print(text_list_check)

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
                            return contents_dy, avatar_path, orig_owner_name, pub_time, type, orig_desc,emoji_list
                        else:
                            return contents_dy, avatar_path, orig_owner_name, orig_pub_time, type, orig_desc,emoji_list
                    orig_url= 'orig_url:'+'https://t.bilibili.com/' + orig_context['id_str']
                    orig_contents,orig_avatar_path,orig_name,orig_Time,orig_type,orig_introduce,orig_emoji_list=await bilibili(orig_url,f'{filepath}orig_',is_twice=True)
                    #print(f'contents:{contents}\norig_contents:{orig_contents}\n')
                    #print(f'emoji_list:{emoji_list}\norig_emoji_list:{orig_emoji_list}')
                    out_path=draw_adaptive_graphic_and_textual(contents, avatar_path=avatar_path,
                                                    name=owner_name, Time=f'{pub_time}', type=type_set,
                                                    introduce=orig_desc,filepath=filepath,
                                                    contents_dy=orig_contents, orig_avatar_path=orig_avatar_path,
                                                    orig_name=orig_name,orig_Time=orig_Time,
                                                    type_software='BiliBili 动态',
                                                    color_software=(251, 114, 153, 80),
                                                    output_path_name=f'{dynamic_id}',avatar_json=avatar_json,
                                                    orig_type_software='转发动态',emoji_list=emoji_list,orig_emoji_list=orig_emoji_list
                                                    )
                    json_check['pic_path'] = out_path
                    json_check['time'] = pub_time
                    return json_check
        return None
    # 直播间识别
    if 'live' in url:
        room_id = re.search(r'\/(\d+)$', url).group(1)
        room = live.LiveRoom(room_display_id=int(room_id))
        data_get_url_context=await room.get_room_info()

        room_info = data_get_url_context['room_info']
        title, cover, keyframe = room_info['title'], room_info['cover'], room_info['keyframe']
        owner_name,owner_cover = data_get_url_context['anchor_info']['base_info']['uname'], data_get_url_context['anchor_info']['base_info']['face']
        area_name,parent_area_name=room_info['area_name'],room_info['parent_area_name']

        #print(f'owner_cover:{owner_cover}\ncover:{cover}')

        if cover =='':
            cover='https://gal.manshuo.ink/usr/uploads/galgame/img/bili-logo.webp'
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
                                      color_software=(251,114,153,80),output_path_name=f'{room_id}',avatar_json=avatar_json)
            json_check['pic_path'] = out_path

            return json_check
        return contents, avatar_path, owner_name, video_time, type, introduce,emoji_list
    # 专栏识别
    if 'read' in url:
        read_id = re.search(r'read\/cv(\d+)', url).group(1)
        ar = article.Article(read_id)
        # 如果专栏为公开笔记，则转换为笔记类
        # NOTE: 笔记类的函数与专栏类的函数基本一致
        if ar.is_note():
            ar = ar.turn_to_note()
        # 加载内容
        await ar.fetch_content()
        #print(ar.markdown())
        markdown_path = f'{filepath}{read_id}.md'
        with open(markdown_path, 'w', encoding='utf8') as f:
            f.write(ar.markdown())
        logger.info('专栏未做识别，跳过，欢迎催更')

        return None
    # 收藏夹识别
    if 'favlist' in url and BILI_SESSDATA != '':

        logger.info('收藏夹未做识别，跳过，欢迎催更')
        return None



    try:
        video_id = re.search(r"video\/[^\?\/ ]+", url)[0].split('/')[1]
        v = video.Video(video_id, credential=credential)
        video_info = await v.get_info()
    except Exception as e:
        logger.info('无法获取视频内容，该进程已退出')
        json_check['status'] = False
        return json_check
    #print(json.dumps(video_info, indent=4))
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
    download_url_data = await v.get_download_url(page_index=page_num)
    detecter = VideoDownloadURLDataDetecter(download_url_data)
    streams = detecter.detect_best_streams()
    try:
        video_url, audio_url = streams[0].url, streams[1].url
        json_check['video_url']=video_url
        json_check['audio_url']=audio_url
    except Exception as e:
        json_check['video_url'] = False



    contents.append((await asyncio.gather(*[asyncio.create_task(download_img(video_cover, f'{filepath}'))]))[0])
    avatar_path = (await asyncio.gather(*[asyncio.create_task(download_img(owner_cover_url, f'{filepath}'))]))[0]

    contents.append(f"{video_title}")
    introduce=f'{video_desc}'

    type=11
    if is_twice is not True:
        out_path=draw_adaptive_graphic_and_textual(contents, avatar_path=avatar_path, name=owner_name,Time=f'{video_time}',type=type,introduce=introduce,
                                    filepath=filepath,type_software='BiliBili',avatar_json=avatar_json,
                                    color_software=(251,114,153,80),output_path_name=f'{video_id}')
        json_check['pic_path'] = out_path
        return json_check
    return contents, avatar_path, owner_name, video_time, type, introduce,emoji_list

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
    json_check = copy.deepcopy(json_init)
    json_check['status'] = True
    json_check['video_url'] = False
    json_check['soft_type'] = 'dy'
    #logger.info(msg)
    # 正则匹配
    reg = r"(http:|https:)\/\/v.douyin.com\/[A-Za-z\d._?%&+\-=#]*"
    dou_url = re.search(reg, msg, re.I)[0]
    dou_url_2 = httpx.get(dou_url).headers.get('location')
    json_check['url'] = dou_url
    logger.info(f'dou_url:{dou_url}')
    #logger.info(f'dou_url_2:{dou_url_2}')

    # 实况图集临时解决方案，eg.  https://v.douyin.com/iDsVgJKL/
    if "share/slides" in dou_url_2:
        cover, author, title, images = await dou_transfer_other(dou_url)
        # 如果第一个不为None 大概率是成功
        if author is not None:
            pass
            #logger.info(f"{GLOBAL_NICKNAME}识别：【抖音】\n作者：{author}\n标题：{title}")
            #logger.info(url for url in images)
        # 截断后续操作
        return
    # logger.error(dou_url_2)
    reg2 = r".*(video|note)\/(\d+)\/(.*?)"
    # 获取到ID
    dou_id = re.search(reg2, dou_url_2, re.I)[2]
    douyin_ck=ini_login_Link_Prising(type=2)
    if douyin_ck is None:
        logger.warning("无法获取到管理员设置的抖音ck！,启用默认配置，若失效请登录")
        douyin_ck='odin_tt=xxx;passport_fe_beating_status=xxx;sid_guard=xxx;uid_tt=xxx;uid_tt_ss=xxx;sid_tt=xxx;sessionid=xxx;sessionid_ss=xxx;sid_ucp_v1=xxx;ssid_ucp_v1=xxx;passport_assist_user=xxx;ttwid=1%7CKPNpSlm-sMOACobI2T3-9GpRhKYzXoy07j_S-KjqxBU%7C1737658644%7Cbec487261896df392f3fe61ed66fa449bbf3f6a88866a7185d2cb17bfc2b8397;'
    # API、一些后续要用到的参数
    headers = {
                  'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                  'referer': f'https://www.douyin.com/video/{dou_id}',
                  'cookie': douyin_ck
              } | COMMON_HEADER
    api_url = DOUYIN_VIDEO.replace("{}", dou_id)
    #logger.info(f'api_url: {api_url}')
    api_url = generate_x_bogus_url(api_url, headers)  # 如果请求失败直接返回
    async with httpx.AsyncClient(headers=headers, timeout=10) as client:
        response = await client.get(api_url)
        detail=response.json()
        if detail is None:
            logger.info(f"{GLOBAL_NICKNAME}识别：抖音，解析失败！")
            # await douyin.send(Message(f"{GLOBAL_NICKNAME}识别：抖音，解析失败！"))
            return
        # 获取信息

        detail = detail['aweme_detail']
        formatted_json = json.dumps(detail, indent=4)
        #print(formatted_json)
        # 判断是图片还是视频
        url_type_code = detail['aweme_type']
        url_type = URL_TYPE_CODE_DICT.get(url_type_code, 'video')
        # 根据类型进行发送
        avatar_url, cover_url = detail['author']['avatar_thumb']['url_list'][0], \
        detail['author']['cover_url'][0]['url_list'][1]
        owner_name = detail['author']['nickname']
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

            player_uri = detail.get("video").get("play_addr")['uri']
            player_real_addr = DY_TOUTIAO_INFO.replace("{}", player_uri)
            #print(player_real_addr)
            json_check['video_url'] = player_real_addr
            #video_path = await download_video(player_real_addr, filepath=filepath)

        elif url_type == 'image':
            # 无水印图片列表/No watermark image list
            no_watermark_image_list = []
            for i in detail['images']:
                no_watermark_image_list.append(i['url_list'][0])
            # logger.info(no_watermark_image_list)
            download_img_funcs = [
                asyncio.create_task(download_img(item, f'{filepath}', len=len(no_watermark_image_list))) for item in
                no_watermark_image_list]
            links_path = await asyncio.gather(*download_img_funcs)
            contents = await add_append_img(contents, links_path)

            # await send_forward_both(bot, event, make_node_segment(bot.self_id, no_watermark_image_list))
            context = detail.get("desc").replace('#', '\n#', 1)
            contents.append(f'{context}')
        out_path = draw_adaptive_graphic_and_textual(contents, avatar_path=avatar_path[0], name=owner_name,
                                                     Time=f'{video_time}', type=11,
                                                     filepath=filepath, type_software='抖音',
                                                     color_software=(0, 0, 0, 80),
                                                     output_path_name=f'{dou_id}')

        json_check['pic_path'] = out_path
        #print(out_path)
        return json_check

async def wb(url,filepath=None):
    json_check = copy.deepcopy(json_init)
    json_check['soft_type'] = 'wb'
    json_check['status'] = True
    json_check['video_url'] = False
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
    # 最终获取到的 id
    weibo_id = weibo_id.split("/")[1] if "/" in weibo_id else weibo_id
    json_check['url'] = f"https://m.weibo.cn/detail/{weibo_id}"
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
        #logger.info(page_info)
        formatted_json = json.dumps(page_info, indent=4)
        #logger.info(formatted_json)
        video_url = page_info.get('urls', '').get('mp4_720p_mp4', '') or page_info.get('urls', '').get('mp4_hd_mp4', '')
        if video_url:
            json_check['video_url'] = video_url
        if 'page_pic' in page_info:
            if page_info.get('type') != 'topic' and page_info.get('type') != 'place':
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
    json_check['pic_path'] = out_path
    return json_check

async def xiaohongshu(url,filepath=None):
    """
        小红书解析
    :param event:
    :return:
    """
    contents=[]
    json_check = copy.deepcopy(json_init)
    json_check['soft_type'] = 'xhs'
    json_check['video_url'] = False
    json_check['status'] = True
    if filepath is None: filepath = filepath_init
    introduce=None
    msg_url = re.search(r"(http:|https:)\/\/(xhslink|(www\.)xiaohongshu).com\/[A-Za-z\d._?%&+\-=\/#@]*",
                        str(url).replace("&amp;", "&").strip())[0]
    # 如果没有设置xhs的ck就结束，因为获取不到
    xhs_ck=ini_login_Link_Prising(type=3)
    if xhs_ck == "" or xhs_ck is None:
        #logger.error(global_config)
        logger.warning('小红书ck未能成功获取，已启用默认配置，若失效请登录')
        xhs_ck='abRequestId=c6f047f3-ec40-5f6a-8a39-6335b5ab7e7e;webBuild=4.55.1;xsecappid=xhs-pc-web;a1=194948957693s0ib4oyggth91hnr3uu4hls0psf7c50000379922;webId=a0f8b87b02a4f0ded2c2c5933780e39e;acw_tc=0ad6fb2417376588181626090e345e91f0d4afd3f1601e0050cac6099b93e4;websectiga=f47eda31ec9%3B545da40c2f731f0630efd2b0959e1dd10d5fedac3dce0bd1e04d;sec_poison_id=3ffe8085-c380-4003-9700-4d63eb6f442f;web_session=030037a0a1c5b6776a218ed7ea204a5d5eaa3b;unread={%22ub%22:%2264676bf40000000027012fbf%22%2C%22ue%22:%2263f40762000000000703bfc2%22%2C%22uc%22:27};gid=yj4j4YjKKDx2yj4j4Yj2W1MiKjqM83D4lvkkMWS9xjyxI828Fq774U888qWjjJJ8y4K4Sif8;'
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
    json_check['url']=msg_url
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
        logger.error(f"{GLOBAL_NICKNAME}识别内容来自：【小红书】\n当前ck已失效，请联系管理员重新设置的小红书ck！")
        #await xhs.send(Message(f"{GLOBAL_NICKNAME}识别内容来自：【小红书】\n当前ck已失效，请联系管理员重新设置的小红书ck！"))
        return
    response_json = response_json.replace("undefined", "null")
    response_json = json.loads(response_json)
    note_data = response_json['note']['noteDetailMap'][xhs_id]['note']
    #print(json.dumps(note_data, indent=4))
    note_title,note_desc,type = note_data['title'],note_data['desc'], note_data['type']

    avatar_path = (await asyncio.gather(*[asyncio.create_task(download_img(note_data['user']['avatar'], f'{filepath}'))]))[0]
    if 'time' in note_data:
        xhs_time=note_data['time']
    elif 'lastUpdateTime' in note_data:
        xhs_time = note_data['lastUpdateTime']
    #logger.info(xhs_time)
    video_time = datetime.utcfromtimestamp(int(xhs_time)/1000) + timedelta(hours=8)
    video_time = video_time.strftime('%Y-%m-%d %H:%M:%S')
    if type == 'normal':
        #logger.info('这是一条解析有文字链接的图文:')
        image_list = note_data['imageList']
        for context in image_list:
            pass
            #logger.info(context["urlDefault"])
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
        json_check['video_url'] = video_url
        image_list = note_data['imageList']
        contents = await add_append_img(contents, await asyncio.gather(
            *[asyncio.create_task(download_img(item['urlDefault'], f'{filepath}', len=len(image_list))) for item in
              image_list]))
        contents.append(f'{note_title}')

    out_path = draw_adaptive_graphic_and_textual(contents, avatar_path=avatar_path, name=note_data['user']['nickname'],
                                                 Time=f'{video_time}', type=11,introduce=introduce,
                                                 filepath=filepath, type_software='小红书',
                                                 color_software=(255, 38, 66, 80),
                                                 output_path_name=f'{xhs_id}')

    json_check['pic_path'] = out_path
    return json_check

async def twitter(url,filepath=None,proxy=None):
    """
        X解析
    :param bot:
    :param event:
    :return:
    """
    msg=url
    contents=[]
    json_check = copy.deepcopy(json_init)
    json_check['soft_type'] = 'x'
    json_check['status'] = True
    json_check['video_url'] = False
    if filepath is None: filepath = filepath_init
    x_url = re.search(r"https?:\/\/x.com\/[0-9-a-zA-Z_]{1,20}\/status\/([0-9]*)", msg)[0]

    x_url = GENERAL_REQ_LINK.replace("{}", x_url)

    # 内联一个请求
    def x_req(url):
        return httpx.get(url, headers={
            'Accept': 'ext/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                      'application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Host': '47.99.158.118',
            'Proxy-Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-User': '?1',
            **COMMON_HEADER
        })
    #print(x_req(x_url).json())
    x_data: object = x_req(x_url).json()['data']

    if x_data is None:
        x_url = x_url + '/photo/1'
        x_data = x_req(x_url).json()['data']
    #print(x_data)

    x_url_res = x_data['url']
    #print(x_url_res)
    #await twit.send(Message(f"{GLOBAL_NICKNAME}识别：小蓝鸟学习版"))

    # 海外服务器判断
    #proxy = None if IS_OVERSEA else resolver_proxy
    logger.info(x_url_res)
    # 图片
    if x_url_res.endswith(".jpg") or x_url_res.endswith(".png"):
        contents = await add_append_img(contents, await asyncio.gather(
            *[asyncio.create_task(download_img(x_url_res, f'{filepath}',proxy=proxy))]))
        #print(contents)
        #res = await download_img(x_url_res, filepath,proxy=proxy)
        out_path = draw_adaptive_graphic_and_textual(contents,type=11,filepath=filepath, type_software='推特',
                                                     color_software=(0, 0, 0, 80),
                                                     output_path_name=f'{int(time.time())}')
        json_check['pic_path'] = out_path
        return json_check
    else:
        # 视频
        json_check['video_url'] = x_url_res
        return json_check
        #res = await download_video(x_url_res, proxy)


async def Galgame_manshuo(url,filepath=None):
    contents=[]
    json_check = copy.deepcopy(json_init)
    json_check['status'] = True
    json_check['video_url'] = False
    if filepath is None: filepath = filepath_init
    link = (re.findall(r"https?://[^\s\]\)]+", url))[0]
    if link =="https://gal.manshuo.ink":return
    context = await html_read(link)
    if '请求发生错误：' in context:
        #print(context)
        json_check['status'] = False
        return json_check
    context = context.split("\n")
    context_check_middle=''
    links_url = None
    Title=''
    avatar_name_flag=0
    time_flag=0
    desc_flag=0
    desc=''
    desc_number=0
    hikarinagi_flag=0
    time_gal='未知'

    if 'gal.manshuo.ink' in url:
        type_software='世伊Galgame论坛'
        type_color=(251, 114, 153, 80)
        avatar_name = '世伊Galgame论坛'
        json_check['soft_type'] = '世伊Galgame论坛'
    elif'www.hikarinagi.com' in url:
        type_software = 'Hikarinagi论坛'
        type_color = (102, 204, 255, 80)
        avatar_name = 'Hikarinagi社区'
        json_check['soft_type'] = 'Hikarinagi论坛'
    elif 'www.mysqil.com' in url:
        type_software = '有希日记'
        type_color = (241, 87, 178, 80)
        avatar_name = '有希日记 - 读书可以改变人生！'
        json_check['soft_type'] = '有希日记'
        try:
            #from plugins.streaming_media_service.Link_parsing.core.selenium_core import scrape_images_get_url
            #links_url_list = scrape_images_get_url(url)
            #links_url = links_url_list[0]
            pass
        except Exception as e:
            links_url = None
            traceback.print_exc()
            print(f"链接获取失败，错误: {e}")


    for context_check in context:
        #print(context_check)
        if time_flag ==1:
            time_flag=2
            time_gal=context_check.replace(" ", "")
            if '[' in context_check:
                time_flag = 1
        if context_check_middle !='':
            if '发表于' in context_check :
                Title=context_check_middle.replace(" ", "")
                time_flag=1
            elif ('[avatar]' in context_check) and time_flag==0:
                Title=context_check_middle.replace(" ", "")
                time_flag=1
        context_check_middle=context_check

        if ('作者:' in context_check or '[avatar]' in context_check) and avatar_name_flag==0:
            avatar_name_flag=1
            if 'https://www.manshuo.ink/img/' in context_check:
                avatar_name_flag = 0
        elif avatar_name_flag==1:
            avatar_name_flag=2
            match = re.search(r"\[(.*?)\]", context_check)
            if match:
                avatar_name=match.group(1).replace(" ", "")

        if '故事介绍' in context_check or '<img src="https://img-static.hikarinagi.com/uploads/2024/08/aca2d187ca20240827180105.jpg"' in context_check:
            if desc_flag == 0:
                desc_flag=1
        elif '[关于](' in context_check and time_flag==2:
            desc_flag=3
        elif 'Hello!有希日記へようこそ!' in context_check:
            #print('检测到标志')
            desc_flag= 10
        elif 'Staff' in context_check:
            desc_flag=0
        elif desc_flag==1:
            context_check=context_check.replace(" ", "")
            if not ('https:'in context_check or 'data:image/svg+xml' in context_check or '插画欣赏' in context_check):
                for i in context_check:
                    desc_number+=1
                if 'ePub格式-连载' in context_check or '作者:' == context_check or '文章链接:' == context_check or '游戏资源' in context_check:
                    desc_flag = 0
                #print(context_check,desc_flag)
                if desc_number > 200 and desc_flag != 0:
                    desc_flag = 0
                    desc +=f'{context_check}…\n'
                else:
                    desc += f'{context_check}\n'
        elif desc_flag != 1:
            desc_flag-=1
        flag = 0
        #print(desc_flag)
        if '登陆后才可以评论获取资源哦～～' in context_check:
            hikarinagi_flag = 1
        elif 'https://gal.manshuo.ink/usr/uploads/galgame/' in context_check:
            if hikarinagi_flag == 0:
                for name_check in {'chara', 'title_page', '图片'}:
                    if f'{name_check}' in context_check: flag = 1
                if flag == 1: continue
                links_url = (re.findall(r"https?://[^\s\]\)]+", context_check))[0]
                image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')
                if not links_url.lower().endswith(image_extensions):
                    links = re.findall(r'\((https?://[^\)]+)\)', context_check)
                    links_url=links[0]
                hikarinagi_flag = 1
        elif 'https://img-static.hikarinagi.com/uploads/' in context_check:
            if hikarinagi_flag == 0:
                links_url = (re.findall(r"https?://[^\s\]\)]+", context_check))[0]
                Title = context_check.replace(" ", "").replace(f"{links_url}", "").replace("[", "").replace("]", "").replace(" - Hikarinagi", "").replace("(", "").replace(")", "")
                hikarinagi_flag=1

    #print(f'links_url:{links_url}')
    if links_url is None:
        try:
            for context_check in context:
                flag = 0
                if 'https://gal.manshuo.ink/usr/uploads/' in context_check:
                    for name_check in {'chara', 'title_page', '图片'}:
                        if f'{name_check}' in context_check: flag = 1
                    if flag == 1: continue
                    #print(f'context_check:{context_check}')
                    links = re.findall(r"https?://[^\s\]\)]+", context_check)
                    #print(f'links:{links}')
                    links_url = links[0]
                    break
        except:
            pass
        finally:
            if links_url is None:
                links_url='https://gal.manshuo.ink/usr/uploads/galgame/zatan.png'
    contents.append(f"title:{Title}")
    contents.append(desc)
    contents = await add_append_img(contents, await asyncio.gather(*[asyncio.create_task(download_img(links_url, f'{filepath}'))]))
    #print(f'final links_url:{links_url}')
    if avatar_name in name_qq_list:
        for name_check in name_qq_list:
            if avatar_name in name_check:
                qq_number=name_qq_list[name_check]
        avatar_path_url=f"https://q1.qlogo.cn/g?b=qq&nk={qq_number}&s=640"
    elif 'www.mysqil.com' in url:
        avatar_path_url = f"https://q1.qlogo.cn/g?b=qq&nk=3231515355&s=640"
    else:
        avatar_path_url='https://gal.manshuo.ink/usr/uploads/galgame/img_master.jpg'


    avatar_path = (await asyncio.gather(*[asyncio.create_task(download_img(avatar_path_url, f'{filepath}'))]))[0]


    json_dy = {'status': False, 'pendant_path': False, 'card_path': False, 'card_number': False, 'card_color': False,
               'card_is_fan': False}

    card_url=card_url_list[random.randint(0,len(card_url_list)-1)]
    json_dy['card_path']=(await asyncio.gather(*[asyncio.create_task(download_img(card_url, f'{filepath}'))]))[0]
    out_path = draw_adaptive_graphic_and_textual(contents, avatar_path=avatar_path, name=avatar_name,
                                                 Time=f'{time_gal}', type=11,
                                                 filepath=filepath, type_software=type_software,avatar_json=json_dy,
                                                 color_software=type_color, output_path_name=f'{int(time.time())}',)
    json_check['pic_path'] = out_path
    return json_check

async def youxi_pil_new_text(filepath=None):
    contents=[]
    json_check = copy.deepcopy(json_init)
    json_check['status'] = True
    json_check['video_url'] = False
    if filepath is None: filepath = filepath_init
    async with httpx.AsyncClient() as client:
        try:
            url_rss = f"https://www.mysqil.com/wp-json/wp/v2/posts"
            response = await client.get(url_rss)
            if response.status_code:
                data = response.json()
                #print(data)
                #print(json.dumps(data[0], indent=4))
                rss_context=data[0]
        except Exception as e:
            json_check['status'] = False
            return json_check
        for rss_text in rss_context:
            #print(rss_text,rss_context[rss_text])
            pass
        #print(rss_context['_links']['author'][0]['href'])
        Title=rss_context['title']['rendered']
        desc = BeautifulSoup(rss_context['excerpt']['rendered'], 'html.parser').get_text().replace(" [&hellip;]", "")
        desc=desc.replace("插画欣赏 作品简介 ", "")
        truncated_text = desc[:200]
        if len(desc) > 200:truncated_text += "..."
        words = truncated_text.split(' ')
        desc_result=''
        for word in words:
            if word !='':
                desc_result+=f'{word}\n'
        #print(desc_result)
        contents.append(f"title:{Title}")
        contents.append(desc_result)

        soup = BeautifulSoup(rss_context['content']['rendered'], 'html.parser')
        data_src_values = [img['data-src'] for img in soup.find_all('img', {'data-src': True})]
        contents = await add_append_img(contents, await asyncio.gather(*[asyncio.create_task(download_img(data_src_values[0], f'{filepath}'))]))

        time_gal=rss_context['date']
        type_software = '有希日记'
        type_color = (241, 87, 178, 80)
        json_check['soft_type'] = '有希日记'
        response = await client.get(rss_context['_links']['author'][0]['href'])
        if response.status_code:
            author_data = response.json()
            #print(json.dumps(author_data, indent=4))
            author_url=author_data['avatar_urls']['96']
            #print(author_url)
            avatar_name=author_data['name']
        avatar_path = (await asyncio.gather(*[asyncio.create_task(download_img(author_url, f'{filepath}'))]))[0]

        json_dy = {'status': False, 'pendant_path': False, 'card_path': False, 'card_number': False,
                   'card_color': False,
                   'card_is_fan': False}

        card_url = card_url_list[random.randint(0, len(card_url_list) - 1)]
        json_dy['card_path'] = (await asyncio.gather(*[asyncio.create_task(download_img(card_url, f'{filepath}'))]))[0]
        out_path = draw_adaptive_graphic_and_textual(contents, avatar_path=avatar_path, name=avatar_name,
                                                     Time=f'{time_gal}', type=11,
                                                     filepath=filepath, type_software=type_software,
                                                     avatar_json=json_dy,
                                                     color_software=type_color,
                                                     output_path_name=f'{int(time.time())}', )
        json_check['pic_path'] = out_path
        #print(json.dumps(json_check, indent=4))
        return json_check


async def bangumi_PILimg(text=None,img_context=None,filepath=None,proxy=None,type_soft='Bangumi 番剧',name=None,url=None,
                         type=None,target=None,search_type=None):
    contents=[]
    json_check = copy.deepcopy(json_init)
    json_check['soft_type'] = 'bangumi'
    json_check['status'] = True
    json_check['video_url'] = False
    if filepath is None: filepath = filepath_init
    if name is not None:
        if os.path.isfile(f'{filepath}{name}.png'):
            json_check['pic_path'] = f'{filepath}{name}.png'
            return json_check
    else:
        name = f'{int(time.time())}'


    if type is None:
        count=0
        count_1=0
        text_add=''
        words = text.split("\n")  # 按换行符分割文本，逐行处理
        for line in words:  # 遍历每一行（处理换行符的部分）
            #print(line)
            count+=1
            text_add+=f'{line}\n'
            if count == len(words):break
            if count % 10 ==0 :
                contents.append(text_add)
                img_add_context =[]
                for i in range(10):
                    img_add_context.append(img_context[i+count_1])
                contents = await add_append_img(contents, await asyncio.gather(*[asyncio.create_task(download_img(item, f'{filepath}', len=len(img_add_context))) for item in img_add_context]))
                text_add = ''
                count_1=count
                await sleep(1)  # 设置好内间隔，以防被冻
        out_path = draw_adaptive_graphic_and_textual(contents,type=11,filepath=filepath, type_software=type_soft,
                                                         color_software=(251, 114, 153, 80),canvas_width=1000,
                                                         output_path_name=name,per_row_pic=5)
        json_check['pic_path'] = out_path
        return json_check
    elif type == 'calendar':
        calendar_json,week = await claendar_bangumi_get_json()
        #print(week)
        #print(json.dumps(calendar_json, indent=4))
        text_total=''
        img_context=[]
        count=0
        for calendar_item in calendar_json:
            #print(calendar_item)
            count+=1
            name_bangumi = calendar_item['name_cn']
            if '' == name_bangumi:
                name_bangumi = calendar_item['name']


            try:
                #img_context.append(calendar_item['images']['common_utils'].replace('http','https'))
                img_context.append(calendar_item['images']['common'].replace('http', 'https'))
                if 'rating' in calendar_item:
                    text_total += f"{count}、 {name_bangumi}----{calendar_item['rating']['score']}☆\n"
                else:
                    text_total += f"{count}、 {name_bangumi}\n"
            except:
                count -= 1
                pass


        count=0
        count_1=0
        text_add=''
        words = text_total.split("\n")  # 按换行符分割文本，逐行处理
        for line in words:  # 遍历每一行（处理换行符的部分）
            #print(line)
            if line == '' :continue
            count+=1
            text_add+=f'{line}\n'
            if count % 10 ==0 :
                contents.append(text_add)
                img_add_context =[]
                for i in range(10):
                    img_add_context.append(img_context[i+count_1])
                contents = await add_append_img(contents, await asyncio.gather(*[asyncio.create_task(download_img(item, f'{filepath}', len=len(img_add_context))) for item in img_add_context]))
                text_add = ''
                count_1=count


        if count % 10 < 10  and count % 10 !=0 and text_add!='':
            img_add_context=[]
            contents.append(text_add)
            for i in range(count % 10):
                img_add_context.append(img_context[i + count_1])
            contents = await add_append_img(contents, await asyncio.gather(*[asyncio.create_task(download_img(item, f'{filepath}', len=len(img_add_context))) for item in img_add_context]))

        #print(contents)
        out_path = draw_adaptive_graphic_and_textual(contents,type=11,filepath=filepath, type_software=type_soft,
                                                         color_software=(251, 114, 153, 80),canvas_width=1000,
                                                         output_path_name=name,per_row_pic=5)
        json_check['pic_path'] = out_path
        json_check['soft_type'] = 'bangumi_calendar'
        return json_check
    elif type == 'search':
        search_json_init = await bangumi_subject_post_json(type=search_type,target=target)
        if search_json_init is False:
            json_check['status'] = False
            return json_check
        search_json=search_json_init['list']

        if int(search_json_init['results']) == 1:
            id = search_json_init['list'][0]['id']
            contents,img_url,contents_other =await bangumi_subjects_get_json_PIL(subject_id=id)
            contents = await add_append_img(contents, await asyncio.gather(*[asyncio.create_task(download_img(img_url, f'{filepath}'))]))
            contents.append(contents_other)
            out_path = draw_adaptive_graphic_and_textual(contents, type=11, filepath=filepath, type_software=type_soft,
                                                         color_software=(251, 114, 153, 80), canvas_width=1000,
                                                         output_path_name=name, per_row_pic=5)
            json_check['pic_path'] = out_path
            json_check['next_choice'] = False
            json_check['soft_type'] = 'bangumi_search'
            return json_check


        id_collect={}
        text_total = ''
        img_context = []
        count = 0
        for search_item in search_json_init['list']:
            count += 1
            id_collect[count] = search_item['id']
            name_bangumi = search_item['name_cn']
            if '' == name_bangumi:
                name_bangumi = search_item['name']
            if 'rating' in search_item:
                text_total += f"{count}、 {name_bangumi}----{search_item['rating']['score']}☆\n"
            else:
                text_total += f"{count}、 {name_bangumi}\n"
            if int(search_json_init['results']) <= 5:
                img_context.append(search_item['images']['large'].replace('http', 'https'))
            else:
                img_context.append(search_item['images']['common_utils'].replace('http', 'https'))

        count = 0
        count_1 = 0
        text_add = ''
        words = text_total.split("\n")  # 按换行符分割文本，逐行处理
        for line in words:  # 遍历每一行（处理换行符的部分）
            if line == '': continue
            count += 1
            text_add += f'{line}\n'
            if count % 10 == 0:
                contents.append(text_add)
                img_add_context = []
                for i in range(10):
                    img_add_context.append(img_context[i + count_1])
                contents = await add_append_img(contents, await asyncio.gather(
                    *[asyncio.create_task(download_img(item, f'{filepath}', len=len(img_add_context))) for item in
                      img_add_context]))
                text_add = ''
                count_1 = count
        if count % 10 < 10  and count % 10 !=0 and text_add!='':
            img_add_context=[]
            contents.append(text_add)
            for i in range(count % 10):
                img_add_context.append(img_context[i + count_1])
            contents = await add_append_img(contents, await asyncio.gather(*[asyncio.create_task(download_img(item, f'{filepath}', len=len(img_add_context))) for item in img_add_context]))

        out_path = draw_adaptive_graphic_and_textual(contents, type=11, filepath=filepath, type_software=type_soft,
                                                     color_software=(251, 114, 153, 80), canvas_width=1000,
                                                     output_path_name=name, per_row_pic=5)
        json_check['pic_path'] = out_path
        json_check['soft_type'] = 'bangumi_search'
        json_check['next_choice'] = True
        json_check['choice_contents'] = id_collect
        #print(id_collect)
        return json_check
    elif type == 'search_accurate':
        contents, img_url, contents_other = await bangumi_subjects_get_json_PIL(subject_id=target)
        contents = await add_append_img(contents, await asyncio.gather(
            *[asyncio.create_task(download_img(img_url, f'{filepath}'))]))
        contents.append(contents_other)
        out_path = draw_adaptive_graphic_and_textual(contents, type=11, filepath=filepath, type_software=type_soft,
                                                     color_software=(251, 114, 153, 80), canvas_width=1000,
                                                     output_path_name=name, per_row_pic=5)
        json_check['pic_path'] = out_path
        json_check['next_choice'] = False
        json_check['soft_type'] = 'bangumi_search'
        return json_check

async def gal_PILimg(text=None,img_context=None,filepath=None,proxy=None,type_soft='Bangumi 番剧',name=None,url=None,
                         type=None,target=None,search_type=None):
    contents=[]
    json_check = copy.deepcopy(json_init)
    json_check['soft_type'] = 'Galgame'
    json_check['status'] = True
    json_check['video_url'] = False
    if filepath is None: filepath = filepath_init
    if name is not None:
        if os.path.isfile(f'{filepath}{name}.png'):
            json_check['pic_path'] = f'{filepath}{name}.png'
            return json_check
    else:
        name = f'{int(time.time())}'
    if type is None:
        title=text.split("gid")[0]
        contents.append(f"title:{title}")
        desc=text.split("简介如下：")[1]
        if '开发商：' in text:
            developer=text.split("开发商：")[1].replace(desc,'').replace('简介如下：','')
            contents.append(f"title:开发商：{developer}")
        contents = await add_append_img(contents, await asyncio.gather(*[asyncio.create_task(download_img(item, f'{filepath}', len=len(img_context))) for item in img_context]))

        contents.append(desc)
        out_path = draw_adaptive_graphic_and_textual(contents,type=11,filepath=filepath, type_software=type_soft,
                                                         color_software=(251, 114, 153, 80),canvas_width=1000,
                                                         output_path_name=name,per_row_pic=5)
        json_check['pic_path'] = out_path
        return json_check


async def majsoul_PILimg(text=None,img_context=None,filepath=None,type_soft='雀魂牌谱屋',canvas_width=1200):
    contents=[]
    json_check = copy.deepcopy(json_init)
    json_check['soft_type'] = '雀魂牌谱屋'
    json_check['status'] = True
    json_check['video_url'] = False
    if filepath is None: filepath = filepath_init

    text_total = ''
    words = text.split("\n")  # 按换行符分割文本，逐行处理
    for line in words:  # 遍历每一行（处理换行符的部分）
        if '昵称：' in line:
            title = line.split("当前段位")[0]
            rating=line.replace(title,'').split('当前pt')[0].replace('当前段位：','').replace(' ','')
            if '当前pt' in line:
                pt_check=line.split('当前pt')[1]
            else:pt_check='未知'
            contents.append(f"title:{title.replace('昵称：','玩家：')}")
            contents.append(f"段位：【{rating}】当前pt{pt_check}")
        elif '查询到多条角色昵称呢~，若输出不是您想查找的昵称，请补全查询昵称' in line:
            contents.append(f'tag:{line}')
        else:
            text_total += f"{line}\n"

    contents.append(text_total)
    if img_context is not None:
        contents = await add_append_img(contents, await asyncio.gather(
            *[asyncio.create_task(download_img(item, f'{filepath}', len=len(img_context))) for item in img_context]))

    out_path = draw_adaptive_graphic_and_textual(contents, type=11, filepath=filepath, type_software=type_soft,
                                                 color_software=(161, 23, 21, 80), canvas_width=canvas_width,
                                                 output_path_name=f'{int(time.time())}', per_row_pic=5)
    json_check['pic_path'] = out_path
    return json_check




async def download_video_link_prising(json,filepath=None,proxy=None):
    if filepath is None:filepath = filepath_init
    video_json={}
    if json['soft_type'] == 'bilibili':
        video_path=await download_b(json['video_url'], json['audio_url'], int(time.time()), filepath=filepath)
    elif json['soft_type'] == 'dy':
        video_path = await download_video(json['video_url'], filepath=filepath)
    elif json['soft_type'] == 'wb':
        video_path = await download_video(json['video_url'], filepath=filepath, ext_headers={
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "referer": "https://weibo.com/"
            })
    elif json['soft_type'] == 'x':
        video_path = await download_video(json['video_url'], filepath=filepath,proxy=proxy)
    elif json['soft_type'] == 'xhs':
        video_path = await download_video(json['video_url'], filepath=filepath)
    video_json['video_path'] = video_path
    file_size_in_mb = get_file_size_mb(video_path)
    if file_size_in_mb < 10:
        video_type='video'
    elif file_size_in_mb < 30:
        video_type='video_bigger'
    elif file_size_in_mb < 100:
        video_type='file'
    else:
        video_type = 'too_big'
    video_json['type']=video_type
    return video_json


async def link_prising(url,filepath=None,proxy=None,type=None):
    json_check = copy.deepcopy(json_init)
    link_prising_json=None
    try:
        url_list = (re.findall(r"https?:[^\s\]\)]+", url))
        for url_check in url_list:
            url=url_check
            if 'b23' in url_check: break
        #print(url)
    except Exception as e:
        json_check['status'] = False
        return json_check
    #print(f'json_init:{json_init}\njson_check:{json_check}\nlink_prising_json:{link_prising_json}\n\n')
    try:
        match url:
            case url if 'bili' in url or 'b23' in url:
                link_prising_json = await bilibili(url, filepath=filepath)
            case url if 'douyin' in url:
                link_prising_json = await dy(url, filepath=filepath)
            case url if 'weibo' in url:
                link_prising_json = await wb(url, filepath=filepath)
            case url if 'xhslink' in url or 'xiaohongshu' in url:
                link_prising_json = await xiaohongshu(url, filepath=filepath)
            case url if 'x.com' in url:
                link_prising_json = await twitter(url, filepath=filepath, proxy=proxy)
            case url if 'gal.manshuo.ink/archives/' in url or 'www.hikarinagi.com' in url :
                link_prising_json = await Galgame_manshuo(url, filepath=filepath)
            case url if 'www.mysqil.com' in url:
                #link_prising_json = await youxi_pil(url, filepath=filepath)
                pass
            case _:
                pass

    except Exception as e:
        json_check['status'] = False
        json_check['reason'] = str(e)
        traceback.print_exc()
        return json_check
    if link_prising_json is not None:
        if type == 'dynamic_check':
            if '编辑于 ' in link_prising_json['time']:
                time_check=link_prising_json['time'].split("编辑于 ")[1].strip()
            else:
                time_check = link_prising_json['time']
            possible_formats = [
                "%Y年%m月%d日 %H:%M",
                "%Y/%m/%d %H:%M",
                "%Y-%m-%d %H:%M",
                "%d-%m-%Y %H:%M",
                "%Y.%m.%d %H:%M",
                "%Y年%m月%d日",
                "%Y/%m/%d",
                "%Y-%m-%d",
                "%d-%m-%Y",
                "%Y.%m.%d",
            ]

            for fmt in possible_formats:
                try:
                    # 尝试解析日期字符串
                    check_time=datetime.strptime(time_check, fmt).strftime("%Y-%m-%d")
                    #print(f"check_time:{check_time}\nnow:{datetime.now().date()}")
                    if str(check_time) != str(datetime.now().date()):
                        link_prising_json['status'] = False
                        link_prising_json['check_time']=check_time
                        #print(f"时间不匹配，拒绝发送 {link_prising_json['time']}\ncheck_time:{check_time}\ndatetime:{datetime.now().date()}")
                    break
                except ValueError:
                    # 如果解析失败，继续尝试下一个格式
                    #traceback.print_exc()
                    continue


        return link_prising_json
    else:
        json_check['status'] = False
        return json_check





#draw_video_thumbnail()
if __name__ == "__main__":#测试用，不用管
    url='https://t.bilibili.com/1032160407411752961?share_source=pc_native'
    #url='97 沉夕cxxx发布了一篇小红书笔记，快来看吧！ 😆 Kde9g1dqG8kAiaG 😆 http://xhslink.com/a/TOydUquIB8p5，复制本条信息，打开【小红书】App查看精彩内容！'
    url='【【温水和彦×八奈见杏菜】用心但不精致的礼物，却意外的收获了笑容-哔哩哔哩】 https://b23.tv/Zm7mYo0'
    #url='【34【PC+KR/gal推荐】《9nine》全系列分享-哔哩哔哩】 https://b23.tv/Um3ewuT'
    #url='https://www.bilibili.com/opus/975425280952762370?spm_id_from=main.mine-history.0.0.pv'
    #url='https://www.bilibili.com/opus/1031855559216726016?plat_id=186&share_from=dynamic&share_medium=iphone&share_plat=ios&share_session_id=3A30238A-7EFA-4778-9339-AEFC6E6BC886&share_source=COPY&share_tag=s_i&spmid=dt.opus-detail.0.0&timestamp=1739177704&unique_k=UfWkGLP'
    url='https://b23.tv/LELSW8u'
    url='https://b23.tv/MNARaEN'
    #url='https://b23.tv/umdU5bb'
    #url='https://b23.tv/waAdNuB'
    #url='https://b23.tv/bicqrKN'
    #url='https://b23.tv/t9YeH0m'
    url='【【明日方舟抽卡】王牌！主播在商店花300凭证单抽出了烛煌！黑子说话！】https://www.bilibili.com/video/BV1dYfUYDE96?vd_source=5e640b2c90e55f7151f23234cae319ec'
    url='https://v.douyin.com/iPhd561x'
    url='https://gal.manshuo.ink/archives/297/'
    url = 'https://www.hikarinagi.com/p/21338'
    url='https://live.bilibili.com/26178650'
    url='https://gal.manshuo.ink/archives/451/'
    url='https://t.bilibili.com/1056778966646390806'

    asyncio.run(link_prising(url))
    #asyncio.run(youxi_pil_new_text())


    url='44 【来抄作业✨早秋彩色衬衫叠穿｜时髦知识分子风 - 杨意子_ | 小红书 - 你的生活指南】 😆 Inw56apL6vWYuoS 😆 https://www.xiaohongshu.com/discovery/item/64c0e9c0000000001201a7de?source=webshare&xhsshare=pc_web&xsec_token=AB8GfF7dOtdlB0n_mqoz61fDayAXpCqWbAz9xb45p6huE=&xsec_source=pc_share'
    url='79 【感谢大数据！椰青茉莉也太太太好喝了吧 - 胖琪琪 | 小红书 - 你的生活指南】 😆 78VORl9ln3YDBKi 😆 https://www.xiaohongshu.com/discovery/item/63dcee03000000001d022015?source=webshare&xhsshare=pc_web&xsec_token=ABJoHbAtOG98_7RnFR3Mf2MuQ1JC8tRVlzHPAG5BGKdCc=&xsec_source=pc_share'
    #asyncio.run(xiaohongshu(url))
    #asyncio.run(link_prising(url))

