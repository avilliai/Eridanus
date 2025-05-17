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
from framework_common.manshuo_draw.core.util.common import printf,printf_check
import gc



async def deal_img(json_img):
    printf_check(json_img)
    printf('开始处理图片')

    #首先创建一个默认长度下的空白png，以便后续裁剪并与背景图粘贴
    deal_img_process = Image.new("RGBA", (json_img['img_width'], json_img['img_height']), (0, 0, 0, 0))



    deal_img_process.save(json_img['img_path_save'], "PNG")
    deal_img_process.show()

    try:#做好对应资源关闭并释放，以免卡顿
        deal_img_process.close()
        del deal_img_process
        gc.collect()
        printf('图片缓存成功释放')
    except:
        printf('绘图资源释放失败，长期可能会导致缓存过大引起卡顿')
