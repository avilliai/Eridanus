import random

import urllib.parse
import os
import shutil
import httpx

"""以下为抖音/TikTok类型代码/Type code for Douyin/TikTok"""
URL_TYPE_CODE_DICT = {
    # 抖音/Douyin
    2: 'image',
    4: 'video',
    68: 'image',
    # TikTok
    0: 'video',
    51: 'video',
    55: 'video',
    58: 'video',
    61: 'video',
    150: 'image'
}

"""
dy视频信息
"""
DOUYIN_VIDEO = "https://www.douyin.com/aweme/v1/web/aweme/detail/?device_platform=webapp&aid=6383&channel=channel_pc_web&aweme_id={}&pc_client_type=1&version_code=190500&version_name=19.5.0&cookie_enabled=true&screen_width=1344&screen_height=756&browser_language=zh-CN&browser_platform=Win32&browser_name=Firefox&browser_version=118.0&browser_online=true&engine_name=Gecko&engine_version=109.0&os_name=Windows&os_version=10&cpu_core_num=16&device_memory=&platform=PC"

"""
今日头条 DY API
"""
DY_TOUTIAO_INFO = "https://aweme.snssdk.com/aweme/v1/play/?video_id={}&ratio=1080p&line=0"

"""
tiktok视频信息
"""
TIKTOK_VIDEO = "https://api22-normal-c-alisg.tiktokv.com/aweme/v1/feed/"
"""
通用请求头
"""
COMMON_HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 '
                  'UBrowser/6.2.4098.3 Safari/537.36'
}


header = {
    'User-Agent': "Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36 Edg/87.0.664.66"
}


def generate_x_bogus_url(url, headers):
    """
            生成抖音A-Bogus签名
            :param url: 视频链接
            :return: 包含X-Bogus签名的URL
            """
    # 调用JavaScript函数
    query = urllib.parse.urlparse(url).query
    abogus_file_path = f'{os.path.dirname(os.path.abspath(__file__))}/a-bogus.js'
    with open(abogus_file_path, 'r', encoding='utf-8') as abogus_file:
        abogus_file_path_transcoding = abogus_file.read()
    import execjs
    abogus = execjs.compile(abogus_file_path_transcoding).call('generate_a_bogus', query, headers['User-Agent'])
    #print('生成的A-Bogus签名为: {}'.format(abogus))
    return url + "&a_bogus=" + abogus


def generate_random_str(self, randomlength=16):
    """
    根据传入长度产生随机字符串
    param :randomlength
    return:random_str
    """
    random_str = ''
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789='
    length = len(base_str) - 1
    for _ in range(randomlength):
        random_str += base_str[random.randint(0, length)]
    return random_str


async def dou_transfer_other(dou_url):
    """
        图集临时解决方案
    :param dou_url:
    :return:
    """
    douyin_temp_data = httpx.get(f"https://api.xingzhige.com/API/douyin/?url={dou_url}").json()
    data = douyin_temp_data.get("data", { })
    item_id = data.get("jx", { }).get("item_id")
    item_type = data.get("jx", { }).get("type")

    if not item_id or not item_type:
        raise ValueError("备用 API 未返回 item_id 或 type")

    # 备用API成功解析图集，直接处理
    if item_type == "图集":
        item = data.get("item", { })
        cover = item.get("cover", "")
        images = item.get("images", [])
        # 只有在有图片的情况下才发送
        if images:
            author = data.get("author", { }).get("name", "")
            title = data.get("item", { }).get("title", "")
            return cover, author, title, images

    return None, None, None, None

if __name__ == '__main__':
    node_path = shutil.which("node")  # 自动查找 Node.js 可执行文件路径
    if not node_path:
        raise EnvironmentError("Node.js 未安装或未正确添加到系统 PATH 中!")

    import execjs
    # 强制使用 Node.js
    execjs._runtime = execjs.ExternalRuntime("Node.js", node_path)
    # 验证是否成功切换到 Node.js
    print(execjs.get().name)  # 应该输出 "Node.js"