from bilibili_api import login, user, sync
import yaml
import os
import urllib.parse
from bilibili_api.login import login_with_password, login_with_sms, send_sms, PhoneNumber, Check
from bilibili_api.user import get_self_info
from bilibili_api import settings
from bilibili_api import sync
import inspect
import asyncio
import shutil
import getpass
from playwright.async_api import async_playwright
import json
from multiprocessing import Lock
import sys
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
class SaveData():
    base_dir = None
    lock = Lock()

    def __init__(self, filename):
        self.filename = os.path.join(self.base_dir, filename + ".json")
        self.data = {}
        self.load()

    def load(self):
        with self.lock:
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as f:
                    self.data = json.load(f)

    def save(self):
        with self.lock:
            if not os.path.exists(self.base_dir):
                os.makedirs(self.base_dir)
            with open(self.filename, 'w') as f:
                json.dump(self.data, f, separators=(',', ':'))

    @classmethod
    def set_base_dir(cls, base):
        cls.base_dir = base


DATA_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
SaveData.set_base_dir(DATA_DIR)

def init_data():  # 初始化文件
    data_file = SaveData("user_data")
    if not data_file.data:
        data_file.data = {
            "login": {},
            "user_info": {},
            "other": {}
        }
    data_file.save()

async def bilibili_login():
    class IgnoreUnknownTagsLoader(yaml.SafeLoader):
        pass
    def ignore_unknown_tags(loader, tag_suffix, node):
        return loader.construct_mapping(node)
    IgnoreUnknownTagsLoader.add_multi_constructor("tag:yaml.org,2002:python/object:", ignore_unknown_tags)

    init_data()
    data_file = SaveData("user_data")
    mode = int(input(
    """请选择登录方式：
    1. 密码登录
    2. 验证码登录
    3. 终端二维码登录
    4. 窗口二维码登录
    请输入 1/2/3/4
    建议使用二维码喵~
    """))


    credential = None
    settings.geetest_auto_open = True

    if mode == 1:
        # 密码登录
        username = input("请输入手机号/邮箱：")
        password = input("请输入密码：")
        print("正在登录。")
        c = login_with_password(username, password)
        if isinstance(c, Check):
            # 还需验证
            phone = print("需要进行验证。请考虑使用二维码登录")
            exit(1)
        else:
            credential = c
        print("登录成功")
    elif mode == 2:
        # 验证码登录
        phone = input("请输入手机号：")
        print("正在登录。")
        send_sms(PhoneNumber(phone, country="+86")) # 默认设置地区为中国大陆
        code = input("请输入验证码：")
        c = login_with_sms(PhoneNumber(phone, country="+86"), code)
        if isinstance(c, Check):
            # 还需验证
            phone = print("需要进行验证。请考虑使用二维码登录")
            exit(1)
        else:
            credential = c
        print("登录成功")
    elif mode == 3:
        credential = login.login_with_qrcode_term()  # 在终端扫描二维码登录
    elif mode == 4:
        credential = login.login_with_qrcode()  # 使用窗口显示二维码登录
    else:
        print("请输入 有效数字！ ！")
        exit()


    try:
        credential.raise_for_no_bili_jct() # 判断是否成功
        credential.raise_for_no_sessdata() # 判断是否成功
    except:
        print("登陆失败。。。")
        exit()

    if credential != None:
        if data_file.data["login"].get(f'bili_login') is None:
            data_file.data['login']['bili_login']={}
        with open(f'{DATA_DIR}/credential.yaml', 'w') as file:
            yaml.dump(credential, file)
        with open(f"{DATA_DIR}/credential.yaml", "r", encoding="utf-8") as file:
            credential_object = yaml.load(file, Loader=IgnoreUnknownTagsLoader)
        data_file.data['login']['bili_login']['ac_time_value']=credential_object['ac_time_value']
        data_file.data['login']['bili_login']['bili_jct'] = credential_object['bili_jct']
        data_file.data['login']['bili_login']['buvid3'] = credential_object['buvid3']
        data_file.data['login']['bili_login']['dedeuserid'] = credential_object['dedeuserid']
        data_file.data['login']['bili_login']['sessdata'] = credential_object['sessdata']
        name = sync(get_self_info(credential))['name']
        print(f"登陆成功，欢迎，{name}!")
    data_file.save()
    if os.path.exists(f'{DATA_DIR}/credential.yaml'):
        os.remove(f'{DATA_DIR}/credential.yaml')


def find_chrome_executable():
    # 查找系统中安装的Chrome浏览器
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(getpass.getuser()),
        shutil.which("chrome"),
        shutil.which("google-chrome")
    ]
    for path in chrome_paths:
        if path and shutil.which(path):
            return path
    raise FileNotFoundError("找不到Chrome浏览器，请手动安装或检查路径。")

async def get_xhs_cookies():
    chrome_path = find_chrome_executable()

    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=False, executable_path=chrome_path)
        page = await browser.new_page()

        # 打开小红书登录页面
        await page.goto('https://www.xiaohongshu.com')


        # 提示用户手动登录
        print("请登录账号后回车确认...")
        input("按回车键继续...")

        # 获取所有cookie
        cookies = await page.context.cookies()
        await browser.close()
        #print(cookies)
        # 将cookie格式化为目标格式
        cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
        required_cookies = [
            "abRequestId", "webBuild", "xsecappid", "a1", "webId",
            "acw_tc", "websectiga", "sec_poison_id", "web_session", "unread",
            "gid"
        ]
        ck_list = [f"{name}={cookie_dict.get(name, 'xxx')}" for name in required_cookies]
        ck_string = ';'.join(ck_list) + ';'
        return ck_string

async def get_douyin_cookies():
    chrome_path = find_chrome_executable()

    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=False, executable_path=chrome_path)
        page = await browser.new_page()

        # 打开抖音登录界面
        await page.goto('https://www.douyin.com')
        # 提示用户手动登录
        print("请登录账号后回车确认...")
        input("按回车键继续...")

        # 获取所有cookie
        cookies = await page.context.cookies()
        await browser.close()
        print(cookies)
        for cookie in cookies:
            print(cookie)
        # 将cookie格式化为目标格式
        cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
        required_cookies = [
            "odin_tt", "passport_fe_beating_status", "sid_guard", "uid_tt", "uid_tt_ss",
            "sid_tt", "sessionid", "sessionid_ss", "sid_ucp_v1", "ssid_ucp_v1",
            "passport_assist_user", "ttwid"
        ]
        ck_list = [f"{name}={cookie_dict.get(name, 'xxx')}" for name in required_cookies]
        ck_string = ';'.join(ck_list) + ';'
        return ck_string

async def douyin_login():
    init_data()
    data_file = SaveData("user_data")
    ck_string = await get_douyin_cookies()
    print("您已成功获取：\n抖音CK:", ck_string)
    if data_file.data["login"].get(f'douyin_login') is None:
        data_file.data['login']['douyin_login'] = {}
    data_file.data['login']['douyin_login']['ck_string'] = ck_string
    data_file.save()

async def xhs_login():
    init_data()
    data_file = SaveData("user_data")
    ck_string = await get_xhs_cookies()
    print("您已成功获取：\n小红书CK:", ck_string)
    if data_file.data["login"].get(f'xhs_login') is None:
        data_file.data['login']['xhs_login'] = {}
    data_file.data['login']['xhs_login']['ck_string'] = ck_string
    data_file.save()


def ini_login_Link_Prising(type=None):
    init_data()
    data_file = SaveData("user_data")
    bili_login_check, douyin_login_check,xhs_login_check=None,None,None
    if type == 1:
        if data_file.data["login"].get(f'bili_login') is not None:
            return data_file.data["login"].get(f'bili_login')
        else:return None
    elif type ==2:
        if data_file.data["login"].get(f'douyin_login') is not None:
            return data_file.data["login"]['douyin_login'].get(f'ck_string')
        else:return None
    elif type ==3:
        if data_file.data["login"].get(f'xhs_login') is not None:
            return data_file.data["login"]['xhs_login'].get(f'ck_string')
        else:return None
    elif type == 0:
        if data_file.data["login"].get(f'bili_login') is not None:
            bili_login_check=True
        if data_file.data["login"].get(f'douyin_login') is not None:
            douyin_login_check=True
        if data_file.data["login"].get(f'xhs_login') is not None:
            xhs_login_check=True
        return bili_login_check,douyin_login_check,xhs_login_check
    data_file.save()

def main():
    ck_string = asyncio.run(get_douyin_cookies())
    print("抖音CK:", ck_string)

async def login_core_select():
    mode = int(input(
    """请选择登录方式：
    1. B站自动登录获取session（暂时不必要）
    2、抖音ck获取（必要）
    3、小红书ck获取（必要）
    """))
    settings.geetest_auto_open = True

    if mode == 1:
        await bilibili_login()
    elif mode ==2:
        try:
            await douyin_login()
        except Exception as e:
            print(e)
    elif mode ==3:
        try:
            await xhs_login()
        except Exception as e:
            print(e)
    else:
        print("请输入 有效数字！ ！")
        exit()

if __name__ == '__main__':
    #bilibili_login()
    #asyncio.run(douyin_login())
    asyncio.run(login_core_select())
    #login_core_select()
    #main()
