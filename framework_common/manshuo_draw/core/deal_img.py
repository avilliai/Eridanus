import asyncio
from PIL import Image, ImageDraw, ImageFont, ImageOps,ImageFilter
import os
import textwrap
import platform
import re
import inspect
from framework_common.manshuo_draw.core.util.download_img_old import download_img
import traceback
import requests
from urllib.parse import urlparse
import gc



from framework_common.manshuo_draw.core.classic_collection import *
from framework_common.manshuo_draw.core.util import *

async def deal_img(json_img): #此函数将逐个解析json文件中的每个字典并与之对应的类相结合
    printf_check(json_img)
    printf('开始处理图片')
    per_number_json=0
    for per_json_img in json_img:               #优先将图片的基本信息创建好，以免出错
        if 'basic_set' in per_json_img['type']:
            basic_img_info = basicimgset(per_json_img)
            basic_img = basic_img_info.creatbasicimgnobackdrop()
            json_img.pop(per_number_json)
            per_number_json = 0
            break
        per_number_json+=1
    for per_json_img in json_img:               #接着处理背景相关
        if 'backdrop' in per_json_img['type']:
            backdrop_class=Backdrop(basic_img_info, per_json_img)
            backdrop_canvas=getattr(backdrop_class, per_json_img['subtype'])()
            json_img.pop(per_number_json)
            break
        per_number_json += 1

    basic_img.paste(backdrop_canvas, (0,0))

    canvas_dict = {}
    number_canvas=0
    for per_json_img in json_img:               #然后考虑处理每个模块之间的关系
        printf(per_json_img)
        number_canvas +=1
        layer_img_info=LayerSet(basic_img_info)
        match per_json_img['type']:
            case 'text':
                Text=TextModule(layer_img_info, per_json_img)
                canvas_dict[number_canvas]=getattr(Text, per_json_img['subtype'])()
                #canvas_dict[number_canvas]['canvas'].show()
            case 'img':
                Image = ImageModule(layer_img_info, per_json_img)
                canvas_dict[number_canvas] = getattr(Image, per_json_img['subtype'])()
            case 'avatar':
                Image = AvatarModule(layer_img_info, per_json_img)
                canvas_dict[number_canvas] = getattr(Image, per_json_img['subtype'])()
            case _:
                #if canvas_dict == {}:return
                pass
        layer_img_canvas=layer_img_info.paste_img(canvas_dict)


    basic_img=basic_img_info.combine_layer_basic(basic_img,layer_img_canvas)


    #首先创建一个默认长度下的空白png，以便后续裁剪并与背景图粘贴
    #deal_img_process = Image.new("RGBA", (json_img['img_width'], json_img['img_height']), (0, 0, 0, 0))

    #img_path = basic_img.img_path_save+"/" + random_str() + ".png"
    #basic_img.save(img_path, "PNG")
    basic_img.show()

    try:#做好对应资源关闭并释放，以免卡顿

        basic_img.close()
        del basic_img



        gc.collect()
        printf('图片缓存成功释放')
    except:
        printf('绘图资源释放失败，长期可能会导致缓存过大引起卡顿')
