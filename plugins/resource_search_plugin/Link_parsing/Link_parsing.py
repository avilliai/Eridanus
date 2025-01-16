from bilibili_api import video, Credential, live, article
from bilibili_api import dynamic
from bilibili_api.opus import Opus
import os
import requests
import re
import httpx
from urllib.parse import urlparse
import asyncio
import os.path
from urllib.parse import parse_qs
from datetime import datetime, timedelta
import json
from plugins.resource_search_plugin.Link_parsing.core.draw import draw_adaptive_graphic_and_textual
from plugins.resource_search_plugin.Link_parsing.core.bili import bili_init,av_to_bv,download_and_process_image
from plugins.resource_search_plugin.Link_parsing.core.weibo import mid2id,WEIBO_SINGLE_INFO
from plugins.resource_search_plugin.Link_parsing.core.common import download_video,download_img,add_append_img
from plugins.resource_search_plugin.Link_parsing.core.tiktok import generate_x_bogus_url, dou_transfer_other, \
    COMMON_HEADER,DOUYIN_VIDEO,URL_TYPE_CODE_DICT,DY_TOUTIAO_INFO
from plugins.resource_search_plugin.Link_parsing.core.login_core import ini_login_Link_Prising
import inspect
import aiohttp

filepath_init=f'{os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(bili_init))))}/data/cache/'
GLOBAL_NICKNAME='Bot'
if not os.path.exists(filepath_init):  # 初始化检测文件夹
        os.makedirs(filepath_init)

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
    #print(f'credential: {credential}')

    if not ( 'bili' in url or 'b23' in url ):return
    #构建绘图消息链
    if filepath is None:
        filepath = filepath_init
        #print(filepath_init)
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
        #print(f'b_short_url:{b_short_url}')
        resp = httpx.get(b_short_url, headers=BILIBILI_HEADER, follow_redirects=True)
        url: str = str(resp.url)
        #print(f'url:{url}')
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
        #print(dynamic_id)
        dy = dynamic.Dynamic(dynamic_id, credential)
        is_opus = dy.is_opus()#判断动态是否为图文

        if is_opus is False:#若判断为图文则换另一种方法读取
            #print('not opus')
            dynamic_info = await Opus(dynamic_id, credential).get_info()
            tags = ''
            if dynamic_info is not None:
                title = dynamic_info['item']['basic']['title']
                paragraphs = []
                for module in dynamic_info['item']['modules']:
                    if 'module_content' in module:
                        paragraphs = module['module_content']['paragraphs']
                        break
                #print(paragraphs)
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
                #print(contents)
                if is_twice is not True:
                    out_path=draw_adaptive_graphic_and_textual(contents, avatar_path=avatar_path, name=owner_name,
                                                  Time=f'{pub_time}',filepath=filepath,type_software='BiliBili 动态',
                                      color_software=(251,114,153,80),output_path_name=f'{dynamic_id}')
                    return out_path,f'https://t.bilibili.com/{dynamic_id}'
                return contents,avatar_path,owner_name,pub_time,type,introduce
            #print(f"{GLOBAL_NICKNAME}识别：B站动态，{title}\n{desc}\n{pics}")

        if is_opus is True:
            dynamic_info = await dy.get_info()
            #print(dynamic_info)
            #print('is opus')
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
                                #print(opus_orig_paragraphs)
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
                    #print(orig_url)


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
        #print(data_get_url_context['room_info'])
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
        #print(room_info['online'])
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
    #print(video_id)
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
        print(f"识别：B站，出错，无法获取数据！")
        return None
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
    #print(msg)
    # 正则匹配
    reg = r"(http:|https:)\/\/v.douyin.com\/[A-Za-z\d._?%&+\-=#]*"
    dou_url = re.search(reg, msg, re.I)[0]
    dou_url_2 = httpx.get(dou_url).headers.get('location')
    print(f'dou_url:{dou_url}')
    #print(f'dou_url_2:{dou_url_2}')

    # 实况图集临时解决方案，eg.  https://v.douyin.com/iDsVgJKL/
    if "share/slides" in dou_url_2:
        cover, author, title, images = await dou_transfer_other(dou_url)
        # 如果第一个不为None 大概率是成功
        if author is not None:
            print(f"{GLOBAL_NICKNAME}识别：【抖音】\n作者：{author}\n标题：{title}")
            print(url for url in images)
        # 截断后续操作
        return
    # logger.error(dou_url_2)
    reg2 = r".*(video|note)\/(\d+)\/(.*?)"
    # 获取到ID
    dou_id = re.search(reg2, dou_url_2, re.I)[2]
    # logger.info(dou_id)
    # 如果没有设置dy的ck就结束，因为获取不到
    douyin_ck=ini_login_Link_Prising(type=2)
    #print(f'douyin_ck: {douyin_ck}')
    if douyin_ck is None:
        print("无法获取到管理员设置的抖音ck！")
        #await douyin.send(Message(f"{GLOBAL_NICKNAME}识别：抖音，无法获取到管理员设置的抖音ck！"))
        return
    # API、一些后续要用到的参数
    headers = {
                  'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                  'referer': f'https://www.douyin.com/video/{dou_id}',
                  'cookie': douyin_ck
              } | COMMON_HEADER
    api_url = DOUYIN_VIDEO.replace("{}", dou_id)
    #print(f'api_url: {api_url}')
    api_url = generate_x_bogus_url(api_url, headers)  # 如果请求失败直接返回
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url, headers=headers, timeout=10) as response:
            detail = await response.json()
            if detail is None:
                print(f"{GLOBAL_NICKNAME}识别：抖音，解析失败！")
                #await douyin.send(Message(f"{GLOBAL_NICKNAME}识别：抖音，解析失败！"))
                return
            # 获取信息
            detail = detail['aweme_detail']
            formatted_json = json.dumps(detail, indent=4)
            #print(formatted_json)
            # 判断是图片还是视频
            url_type_code = detail['aweme_type']
            url_type = URL_TYPE_CODE_DICT.get(url_type_code, 'video')
            #print(f"{GLOBAL_NICKNAME}识别：抖音，{detail.get('desc')}")
            # 根据类型进行发送
            avatar_url,cover_url=detail['author']['avatar_thumb']['url_list'][0],detail['author']['cover_url'][0]['url_list'][1]
            owner_name=detail['author']['nickname']
            #print(f'avatar_url: {avatar_url}\ncover_url: {cover_url}')
            download_img_funcs = [asyncio.create_task(download_img(avatar_url, f'{filepath}'))]
            avatar_path = await asyncio.gather(*download_img_funcs)
            video_time = datetime.utcfromtimestamp(detail['create_time']) + timedelta(hours=8)
            video_time = video_time.strftime('%Y-%m-%d %H:%M:%S')

            if url_type == 'video':
                # 识别播放地址
                player_uri = detail.get("video").get("play_addr")['uri']
                player_real_addr = DY_TOUTIAO_INFO.replace("{}", player_uri)
                cover_url = detail.get("video").get("dynamic_cover")['url_list'][0]
                #print(f'cover_url: {cover_url}\nplayer_real_addr: {player_real_addr}')
                download_img_funcs = [asyncio.create_task(download_img(cover_url, f'{filepath}'))]
                cover_path = await asyncio.gather(*download_img_funcs)
                #print(cover_path)
                contents = await add_append_img(contents, cover_path)
                context = detail.get("desc").replace('#', '\n#', 1)
                contents.append(f'{context}')

            elif url_type == 'image':
                # 无水印图片列表/No watermark image list
                no_watermark_image_list = []
                for i in detail['images']:
                    no_watermark_image_list.append(i['url_list'][0])
                #print(no_watermark_image_list)
                download_img_funcs = [asyncio.create_task(download_img(item, f'{filepath}',len=len(no_watermark_image_list)))for item in no_watermark_image_list]
                links_path = await asyncio.gather(*download_img_funcs)
                #print(links_path)
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
        print(match)
        if match:
            get_url = match.group(2)
            print(get_url)
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
        print("解析失败：无法获取到wb的id")
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
    #print(formatted_json)
    text, status_title, source, region_name, pics, page_info = (weibo_data.get(key, None) for key in
                                                                ['text', 'status_title', 'source', 'region_name',
                                                                 'pics', 'page_info'])
    owner_name,avatar_hd,video_time=weibo_data['user']['screen_name'],weibo_data['user']['avatar_hd'],weibo_data['created_at']
    download_img_funcs = [asyncio.create_task(download_img(avatar_hd, f'{filepath}',
                          headers={"Referer": "http://blog.sina.com.cn/"} | COMMON_HEADER))]
    avatar_path = await asyncio.gather(*download_img_funcs)
    # 发送消息
    #print(f"{GLOBAL_NICKNAME}识别：微博，{re.sub(r'<[^>]+>', '', text)}\n{status_title}\n{source}\t{region_name if region_name else ''}")
    #print(f'source:{source}\nregion_name:{region_name}')
    content.append(re.sub(r'<[^>]+>', '', text))

    if pics:
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
        #print(page_info)
        if 'page_pic' in page_info:
            page_pic=page_info.get('page_pic').get('url')
            #print(page_pic)
            download_img_funcs = [asyncio.create_task(download_img(page_pic, f'{filepath}',headers={ "Referer": "http://blog.sina.com.cn/"} | COMMON_HEADER))]
            page_pic_path = await asyncio.gather(*download_img_funcs)
            content.append(page_pic_path[0])

    out_path = draw_adaptive_graphic_and_textual(content, avatar_path=avatar_path[0], name=owner_name,
                                                 Time=f'{video_time}', type=11,
                                                 filepath=filepath, type_software='微博',
                                                 color_software=(255, 92, 0, 80),
                                                 output_path_name=f'{weibo_id}')
    return out_path, None


async def link_prising(url,filepath=None):
    dy_path=None
    if 'bili' in url or 'b23' in url:
        dy_path,url=await bilibili(url,filepath=filepath)
    elif 'douyin' in url or 'douyin' in url:
        dy_path,url=await dy(url, filepath=filepath)
    elif 'weibo' in url:
        dy_path,url=await wb(url, filepath=filepath)
    return dy_path,url

#draw_video_thumbnail()
if __name__ == "__main__":#测试用，不用管
    url='https://t.bilibili.com/1020853339034746883?share_source=pc_native'
    url='https://t.bilibili.com/1021014297223888949?share_source=pc_native'
    url='7.48 复制打开抖音，看看【路过的路人的作品】小厨男天天被我玩# 兔娘 # cos # 超时空跑... https://v.douyin.com/iypyEDf1/ 08/27 p@q.Rk baa:/ '
    #url='7.66 11/02 O@K.Wm Bte:/ 2命大黑塔梦幻排轴17动（创作服大黑塔电子榨菜第三期） 你不觉得17这个数字很梦幻吗？当然这都是为了给您展示2命的多动，纯属娱乐玩法，正常来说，攻击绳子，攻击鞋，全输出走起~怪根本扛不住！ # 崩坏星穹铁道 # 在第八日启程# 星穹铁道创作服前瞻 # 大黑塔 # 游戏内容风向标  https://v.douyin.com/iypveGXJ/ 复制此链接，打开Dou音搜索，直接观看视频！'
    #url='0.02 ZZM:/ a@N.WM 10/20 大黑塔基础玩法技能遗器详细介绍！（创作服大黑塔第二期） 本期视频涵盖了很多，本身大黑塔的细节较多，所以不得已的给各位上了几个表，应该不至于太催眠，希望能帮助大家更好的理解这个角色，有问题和想法欢迎评论区指出，有赖各位观众支持小河马! # 崩坏星穹铁道 # 在第八日启程# 星穹铁道创作服前瞻 # 游戏内容风向标 # 大黑塔  https://v.douyin.com/iytXUdEG/ 复制此链接，打开Dou音搜索，直接观看视频！'
    url='0.02 08/14 v@s.Eh cNW:/ 抖音图文怎么发。回复 @用户6901949649936的评论 抖音图片左滑动怎么制作，抖音图片左右滑动翻页视频怎么制作。抖音图文关闭音乐卡点，切换速度就会变慢。  https://v.douyin.com/if1L82W3/ 复制此链接，打开Dou音搜索，直接观看视频！'
    url='6.17 复制打开抖音，看看【兔娘的面首的作品】不要彩礼 # 兔娘 # 兔娘直播回放 # 御姐 #... https://v.douyin.com/iy38a4Dk/ P@X.MW OXm:/ 09/09 '
    #asyncio.run(dy(url))
    url='【TikTok，能活下来么？】https://www.bilibili.com/video/BV1JccNerEYx?vd_source=5e640b2c90e55f7151f23234cae319ec'
    url='https://t.bilibili.com/1019576501083832328?share_source=pc_native'
    url='https://t.bilibili.com/1022796124533030914?share_source=pc_native'
    url='https://t.bilibili.com/1022795905498087445?share_source=pc_native'
    url='https://t.bilibili.com/1022767709046177793?share_source=pc_native'
    url='https://t.bilibili.com/1022904074263068729?share_source=pc_native'
    asyncio.run(bilibili(url))
    url='https://weibo.com/2219124641/5121698360208427'
    url='https://weibo.com/2399108147/5123063479535033'
    url='https://weibo.com/7480686919/5123066430754791'
    #asyncio.run(wb(url))

