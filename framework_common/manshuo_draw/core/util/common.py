import random
import string


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