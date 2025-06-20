import random
import string
import re
import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageOps,ImageFilter
import platform

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
            if 'debug' in key_json and key_json['debug'] is True:
                debug_mode = True
                print('本次绘图已开启调试功能')
                break

def random_str(length=10):
    characters = string.ascii_letters + string.digits
    # 生成随机字符串
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string




def get_abs_path(path,is_ignore_judge=False):
    if is_ignore_judge:
        # 判断路径是否为绝对路径
        if not os.path.isabs(path):
            # 如果是相对路径，将其转换为绝对路径
            upper_dir = os.path.abspath(__file__)
            for _ in range(5):  # 寻找上五级的目录，即为Eridanus
                upper_dir = os.path.dirname(upper_dir)
            absolute_path = os.path.join(upper_dir, path)
            return absolute_path
        else:
            # 如果已经是绝对路径，则直接返回
            return path

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
        return absolute_path
    else:
        # 如果已经是绝对路径，则直接返回
        return path



def crop_to_square(img_list):
    """
    将一个 Pillow 图像对象裁剪为居中的正方形。
    """
    img_processed_list = []
    for image in img_list:
        width, height = image.size
        # 计算短边的边长，即正方形的边长
        side_length = min(width, height)

        # 计算裁剪区域（左、上、右、下）
        left = (width - side_length) // 2
        top = (height - side_length) // 2
        right = left + side_length
        bottom = top + side_length

        # 裁剪图像
        cropped_image = image.crop((left, top, right, bottom))
        img_processed_list.append(cropped_image)

    return img_processed_list










if __name__ == '__main__':
    path='framework_common/manshuo_draw/data/fort/LXGWWenKai-Regular.ttf'
    color_emoji_maker('❤️',(0,0,0))