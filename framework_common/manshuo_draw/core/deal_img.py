import asyncio
from PIL import Image, ImageDraw, ImageFont, ImageOps,ImageFilter
import os
import textwrap
import platform
import re
import inspect
from framework_common.manshuo_draw.core.util.download_img import download_img
import traceback
import requests
from urllib.parse import urlparse
import gc



from framework_common.manshuo_draw.core.classic_collection import *
from framework_common.manshuo_draw.core.util import *

async def deal_img(json_img): #此函数将逐个解析json文件中的每个字典并与之对应的类相结合
    printf_check(json_img)
    printf('开始处理图片')

    for per_json_img in json_img:
        printf(per_json_img)
        if 'basic_set' in per_json_img['type']:
            basic_img_no_backdrop=basicimgset(per_json_img)
            deal_img_process=basic_img_no_backdrop.creatbasicimgnobackdrop()


    #首先创建一个默认长度下的空白png，以便后续裁剪并与背景图粘贴
    #deal_img_process = Image.new("RGBA", (json_img['img_width'], json_img['img_height']), (0, 0, 0, 0))

    img_path = basic_img_no_backdrop.img_path_save+"/" + random_str() + ".png"
    deal_img_process.save(img_path, "PNG")
    deal_img_process.show()

    try:#做好对应资源关闭并释放，以免卡顿
        deal_img_process.close()
        del deal_img_process
        gc.collect()
        printf('图片缓存成功释放')
    except:
        printf('绘图资源释放失败，长期可能会导致缓存过大引起卡顿')
