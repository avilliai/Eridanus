import random
import string
import re
import os
import sys

global debug_mode #设定全局变量，表示绘图是否开启调试功能
debug_mode = False

def printf(text):
    if debug_mode:
        print(text)

def printf_check(json_img):
    global debug_mode
    for key_json in json_img:
        #print(key_json)
        if key_json['type'] == 'basic_set':
            if key_json['debug'] is True:
                debug_mode = True
                print('本次绘图已开启调试功能')
                break

def random_str(length=10):
    characters = string.ascii_letters + string.digits
    # 生成随机字符串
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string


def extract_string(input_string, tag):
    #仿照markdown语法提取特定字符串，格式为[tag]anything[/tag],并返回提取内容和清除提取内容后的源文本
    # 构造正则表达式，匹配 [tag]内容[/tag]
    pattern = rf"\[{tag}\](.*?)\[/{tag}\]"

    # 提取内容
    match = re.search(pattern, input_string)
    if match:
        extracted_content = match.group(1)  # 获取匹配到的内容
        # 清除标签和内容
        cleaned_string = re.sub(pattern, "", input_string)  # 替换匹配的部分为空字符串
        return extracted_content, cleaned_string
    else:
        return "", input_string  # 如果没有匹配到，返回空内容和原字符串

def get_abs_path(path):
    """获取绝对路径"""
    #判断传入的是否为路径
    if not (isinstance(path, str) and os.path.splitext(path)[1].lower() in [".jpg", ".png", ".jpeg", '.webp',".ttf",".yaml"]):
        return path

    try:
        os.path.normpath(path)  # 尝试规范化路径
    except Exception:
        return path  # 出现异常，则路径无效

    # 判断路径是否为绝对路径
    if not os.path.isabs(path):
        # 如果是相对路径，将其转换为绝对路径
        upper_dir = os.path.abspath(__file__)
        for _ in range(5):#寻找上五级的目录，即为Eridanus
            upper_dir = os.path.dirname(upper_dir)
        absolute_path = os.path.join(upper_dir, path)
        #print(f"'{path}' 是相对路径，\n已转换为绝对路径：'{absolute_path}'")
        return absolute_path
    else:
        # 如果已经是绝对路径，则直接返回
        #print(f"'{path}' 已经是绝对路径")
        return path

if __name__ == '__main__':
    path='framework_common/manshuo_draw/data/fort/LXGWWenKai-Regular.ttf'
    path_processed=get_abs_path(path)