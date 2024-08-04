import logging
import random
import re

import colorlog
import httpx
import requests
import yaml
from lanzou.api import LanZouCloud

'''此处用以集合常用的工具
lanzouFileToUrl(path) 用以上传文件转直链
newLogger()           日志需要用到，如果你需要logger，调用即可
async translate(text,mode="ZH_CN2JA")  翻译接口，文本，以及翻译模式。需要异步调用
random_str()          生成六位随机字符串，用以文件命名
get_headers()         返回一个UA，网络请求使用
check_cq_atcode(event.raw_message,bot.id)  检查CQ码中是否包含at bot的信息
extract_image_urls(event.raw_message)      返回event.raw_message中所有图片的url
'''
with open('config/api.yaml', 'r', encoding='utf-8') as f:
    apiYaml = yaml.load(f.read(), Loader=yaml.FullLoader)

lzy = LanZouCloud()
cookie = {'ylogin': str(apiYaml.get("蓝奏云").get("ylogin")), 'phpdisk_info': apiYaml.get("蓝奏云").get("phpdisk_info")}
code=lzy.login_by_cookie(cookie)


def lanzouFileToUrl(path):
    url=""
    def show_progress(file_name, total_size, now_size):
        percent = now_size / total_size
        bar_len = 40  # 进度条长总度
        bar_str = '>' * round(bar_len * percent) + '=' * round(bar_len * (1 - percent))
        print('\r{:.2f}%\t[{}] {:.1f}/{:.1f}MB | {} '.format(
            percent * 100, bar_str, now_size / 1048576, total_size / 1048576, file_name), end='')
        if total_size == now_size:
            print('')  # 下载完成换行

    def handler(fid, is_file):
        nonlocal url  # 声明要修改外部函数的url变量
        r=lzy.get_durl_by_id(fid)
        url=r.durl
    lzy.upload_file(path, -1, callback=show_progress,uploaded_handler=handler)
    return url
def createLogger():
    # 创建一个logger对象
    logger = logging.getLogger("Manayana")
    # 设置日志级别为DEBUG，这样可以输出所有级别的日志
    logger.setLevel(logging.DEBUG)
    # 创建一个StreamHandler对象，用于输出日志到控制台
    console_handler = logging.StreamHandler()
    # 设置控制台输出的日志格式和颜色
    logger.propagate = False
    console_format = '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    console_colors = {
        'DEBUG': 'white',
        'INFO': 'cyan',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
    console_formatter = colorlog.ColoredFormatter(console_format, log_colors=console_colors)
    console_handler.setFormatter(console_formatter)
    # 将控制台处理器添加到logger对象中
    logger.addHandler(console_handler)
    # 使用不同级别的方法来记录不同重要性的事件
    '''logger.debug('This is a debug message')
    logger.info('This is an info message')
    logger.warning('This is a warning message')
    logger.error('This is an error message')
    logger.critical('This is a critical message')'''
    return logger
async def translate(text, mode="ZH_CN2JA"):
    try:
        URL = f"https://api.pearktrue.cn/api/translate/?text={text}&type={mode}"
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(URL)
            #print(r.json()["data"]["translate"])
            return r.json()["data"]["translate"]
    except:
        print("文本翻译接口1失效")
        if mode != "ZH_CN2JA":
            return text
    try:
        url = f"https://findmyip.net/api/translate.php?text={text}&target_lang=ja"
        r = requests.get(url=url, timeout=10)
        return r.json()["data"]["translate_result"]
    except:
        print("翻译接口2调用失败")
    try:
        url = f"https://translate.appworlds.cn?text={text}&from=zh-CN&to=ja"
        r = requests.get(url=url, timeout=10, verify=False)
        return r.json()["data"]
    except:
        print("翻译接口3调用失败")
    return text
def random_str(random_length=6, chars='AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789@$#_%'):
    """
    生成随机字符串作为验证码
    :param random_length: 字符串长度,默认为6
    :return: 随机字符串
    """
    string = ''

    length = len(chars) - 1
    # random = Random()
    # 设置循环每次取一个字符用来生成随机数
    for i in range(7):
        string += (chars[random.randint(0, length)])
    return string
def get_headers():
    user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"]

    userAgent = random.choice(user_agent_list)
    headers = {'User-Agent': userAgent}
    return headers

def check_cq_atcode(cq_code, bot_qq):
    # 正则表达式匹配 [CQ:at,qq=bot_qq]
    match = re.search(r'\[CQ:at,qq=(\d+)\]', cq_code)
    if match:
        qq_number = match.group(1)
        if qq_number == str(bot_qq):
            # 使用正则表达式去除所有 CQ 码部分
            message = re.sub(r'\[.*?\]', '', cq_code).strip()
            return message
    return False
def extract_image_urls(text):
    # 正则表达式匹配所有 CQ:image 并提取 url 参数的值
    urls = re.findall(r'\[CQ:image,[^\]]*url=([^,^\]]+)', text)

    if urls:
        return urls
    return None
logger=createLogger()
def newLogger():
    return logger