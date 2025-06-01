from io import BytesIO

import httpx
import asyncio
import os
import re
import urllib.parse

from PIL import Image

from framework_common.framework_util.yamlLoader import YAMLManager

# 全局变量
DOWNLOAD_LIMIT = 5  # 获取到的视频数量，或者信息条数
API_BASE_URL = "https://api.iwara.tv/videos"
RATING = "all"  # ecchi(r18), all（没啥用，因为就没有不是r18的）
DOWNLOAD_DIR = "data/pictures/cache"  # 视频下载目录


yaml_manager = YAMLManager.get_instance()

local_config = yaml_manager.common_config.basic_config
proxy = local_config.get("proxy").get("http_proxy")
if not proxy:
    proxy = None

def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)

async def download_video(client, video_id):
    print(f"\n正在处理视频 ID: {video_id}")
    video_details_url = f"https://api.iwara.tv/video/{video_id}"
    print(f"从以下地址获取详情: {video_details_url}")
    video_response = await client.get(video_details_url)
    video_response.raise_for_status()
    video_data = video_response.json()
    
    title = video_data.get("title")
    file_url = video_data.get("fileUrl")
    
    if not file_url:
        print(f"未找到视频 ID: {video_id} 的文件 URL")
        return None
    
    download_links_response = await client.get(file_url)
    download_links_response.raise_for_status()
    
    download_links = download_links_response.json()
    
    if not download_links or len(download_links) == 0:
        print(f"未找到视频 ID: {video_id} 的下载链接")
        return None
    
    # 查找 '360' 质量的下载链接
    first_download_link = None
    for link in download_links:
        if link.get("name") == "360":
            first_download_link = link["src"].get("download")
            break
    
    if not first_download_link:
        print(f"未找到视频 ID: {video_id} 的 '360' 质量下载链接")
        return None
    
    full_download_url = f"https:{first_download_link}"
    print(f"开始下载视频: {full_download_url}")
    
    async with client.stream('GET', full_download_url, follow_redirects=True) as response:
        response.raise_for_status()
        sanitized_title = sanitize_filename(title)
        file_name = f"{sanitized_title}.mp4"
        absolute_file_path = os.path.abspath(os.path.join(DOWNLOAD_DIR, file_name)).replace("\\", "/")
        os.makedirs(os.path.dirname(absolute_file_path), exist_ok=True)
        with open(absolute_file_path, 'wb') as f:
            async for chunk in response.aiter_bytes():
                f.write(chunk)
    
    print(f"视频已下载并保存为: {absolute_file_path}")
    return {
        "title": title,
        "video_id": video_id,
        "path": absolute_file_path
    }

async def fetch_video_info(sort,config):
    url = f"{API_BASE_URL}?rating={RATING}&sort={sort}&limit={DOWNLOAD_LIMIT}"
    if proxy:
        proxies = {"http://": proxy, "https://": proxy}
    else:
        proxies = None
    async with httpx.AsyncClient(timeout=None,proxies=proxies) as client:
        #print(f"发送初始请求到: {url}")
        response = await client.get(url)
        response.raise_for_status()  # 检查请求是否成功
        #print(f"初始请求成功, 状态码: {response.status_code}")
        
        data = response.json()
        results = data.get("results", [])
        #print(f"获取到的视频数量: {len(results)}")
        
        video_info_list = []
        
        for item in results:
            video_info = await process_video(client, item)
            if video_info:
                video_info_list.append(video_info)
        
        '''print("\n最终视频信息列表:")
        for video_info in video_info_list:
            print(video_info)'''
        return video_info_list

async def process_video(client, item,iwara_gray_layer=False):
    title = item.get("title")
    video_id = item.get("id")
    
    if not title or not video_id:
        #print(f"缺少必要的字段: 视频 ID: {video_id}, 标题: {title}")
        return None
    
    #print(f"\n正在处理视频 ID: {video_id}, 标题: {title}")
    
    thumbnail_path = await download_thumbnail(client, item,iwara_gray_layer)
    
    return {
        "title": title,
        "video_id": video_id,
        "path": thumbnail_path
    }

async def download_thumbnail(client, item,iwara_gray_layer):
    title = item.get("title")
    thumbnail = item.get("thumbnail", 0)
    file_data = item.get("file", {})
    video_id = file_data.get("id")
    custom_thumbnail = item.get("customThumbnail")
    
    if not title or not video_id:
        #print(f"缺少必要的字段: 视频 ID: {video_id}, 标题: {title}")
        return None
    
    #print(f"\n正在处理视频 ID: {video_id}, 标题: {title}")
    
    if custom_thumbnail and custom_thumbnail.get("id"):
        thumbnail_id = custom_thumbnail.get("id")
        thumbnail_url = f"https://i.iwara.tv/image/thumbnail/{thumbnail_id}/{thumbnail_id}.jpg"
        #print(f"尝试下载自定义缩略图 URL: {thumbnail_url}")
        
        try:

            response = await client.get(thumbnail_url)
            response.raise_for_status()
            print(f"自定义缩略图内容请求成功, 状态码: {response.status_code}")
            
            sanitized_title = sanitize_filename(title)
            file_name = f"{sanitized_title}.jpg"
            absolute_file_path = os.path.abspath(os.path.join(DOWNLOAD_DIR, file_name)).replace("\\", "/")
            os.makedirs(os.path.dirname(absolute_file_path), exist_ok=True)

            with open(absolute_file_path, 'wb') as f:
                f.write(response.content)

            return absolute_file_path

        except httpx.HTTPStatusError as e:
            #print(f"自定义缩略图 URL 请求失败: {e}")
            return None
    else:
        thumbnail_padded = f"{int(thumbnail):02d}"  # 如果 thumbnail 为 0，则结果为 "00"
        thumbnail_url = f"https://i.iwara.tv/image/thumbnail/{video_id}/thumbnail-{thumbnail_padded}.jpg"
        #print(f"尝试下载缩略图 URL: {thumbnail_url}")
        
        try:
            response = await client.get(thumbnail_url)
            sanitized_title = sanitize_filename(title)
            file_name = f"{sanitized_title}.jpg"
            absolute_file_path = os.path.abspath(os.path.join(DOWNLOAD_DIR, file_name)).replace("\\", "/")
            os.makedirs(os.path.dirname(absolute_file_path), exist_ok=True)
            img = Image.open(BytesIO(response.content))  # 从二进制数据创建图片对象
            if iwara_gray_layer:
                #print(f"缩略图内容请求成功, 状态码: {response.status_code}")
                image_raw = img
                image_black_white = image_raw.convert('1')
                image_black_white.save(absolute_file_path)
            else:
                img.save(absolute_file_path)
            
            #print(f"缩略图已下载并保存为: {absolute_file_path}")
            return absolute_file_path
        except httpx.HTTPStatusError as e:
            #print(f"缩略图 URL 请求失败: {e}")
            return None

async def rank_videos(sort,config):
    url = f"{API_BASE_URL}?rating={RATING}&sort={sort}&limit={DOWNLOAD_LIMIT}"
    if proxy:
        proxies = {"http://": proxy, "https://": proxy}
    else:
        proxies = None
    async with httpx.AsyncClient(timeout=None,proxies=proxies) as client:
        #print(f"发送排行请求到: {url}")
        response = await client.get(url)
        response.raise_for_status()  # 检查请求是否成功
        #print(f"排行请求成功, 状态码: {response.status_code}")
        
        data = response.json()
        results = data.get("results", [])
        #print(f"获取到的视频数量: {len(results)}")
        
        video_download_list = []
        
        for item in results:
            video_info = await download_video(client, item.get("id"))
            if video_info:
                video_download_list.append(video_info)
        
        #print("\n最终视频下载列表:")
        #for video_info in video_download_list:
            #print(video_info)

async def download_specific_video(videoid,config):
    if proxy:
        proxies = {"http://": proxy, "https://": proxy}
    else:
        proxies = None
    async with httpx.AsyncClient(timeout=None,proxies=proxies) as client:
        video_info = await download_video(client, videoid)
        if video_info:
            #print("\n最终视频下载信息:")
            #print(video_info)
            return video_info
        else:
            return None
            #print(f"未能下载视频 ID: {videoid}")
            
async def search_videos(word,config,iwara_gray_layer=False):
    query = urllib.parse.quote(word)
    url = f"https://api.iwara.tv/search?type=video&page=0&query={query}&limit={DOWNLOAD_LIMIT}"
    if proxy:
        proxies = {"http://": proxy, "https://": proxy}
    else:
        proxies = None
    async with httpx.AsyncClient(timeout=None,proxies=proxies) as client:
        #print(f"发送搜索请求到: {url}")
        response = await client.get(url)
        response.raise_for_status()  # 检查请求是否成功
        #print(f"搜索请求成功, 状态码: {response.status_code}")
        
        data = response.json()
        results = data.get("results", [])
        #print(f"获取到的视频数量: {len(results)}")
        
        video_info_list = []
        
        for item in results:
            video_info = await process_video(client, item, iwara_gray_layer)
            if video_info:
                video_info_list.append(video_info)
        
        #print("\n最终视频信息列表:")
        #for video_info in video_info_list:
            #print(video_info)
        return video_info_list

def main(command):
    if command.startswith("下载"):
        videoid = command.replace("下载", "").strip()
        if videoid:
            asyncio.run(download_specific_video(videoid))
        else:
            return None
            #print("请输入有效的视频ID。")
    elif command.startswith("搜索"):
        word = command.replace("搜索", "").strip()
        if word:
            asyncio.run(search_videos(word))
        else:
            return None
            #print("请输入有效的搜索关键词。")
    elif command.startswith("榜单下载"):
        sort = command.replace("榜单", "").strip()
        asyncio.run(rank_videos(sort))
    elif command.startswith("榜单"):
        sort = command.replace("榜单", "").strip()
        asyncio.run(fetch_video_info(sort))
        #print("未知命令，请输入 '榜单{name}'、'榜单下载{name}' 、'下载{video_id}、'搜索{关键词}'")

if __name__ == "__main__":
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)  # 创建下载目录
    while True:
        print("\nname可以是date(最新), popularity(热门), trending(趋势);所有结果个数为DOWNLOAD_LIMIT(代码开头去改)\n用的时候不要带大括号")
        command = input("请输入命令 (榜单{name}/榜单下载{name}/下载{video_id}/搜索{关键词}): ")
        main(command)
