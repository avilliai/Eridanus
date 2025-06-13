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


async def layer_deal(basic_img_info,json_img,layer=1):

    layer_img_info = LayerSet(basic_img_info)

    json_img_processed=[]
    i = 0
    while i < len(json_img):
        per_json_img=json_img[i]

        if 'layer' not in per_json_img:layer_check=1
        else:layer_check=per_json_img['layer']
        if layer_check == layer:
            json_img_processed.append(per_json_img)
            json_img.pop(json_img.index(per_json_img))

        elif layer_check > layer:
            json_check=await layer_deal(layer_img_info,json_img,layer=layer+1)

            json_img_processed.append({'type':'layer_processed','content':json_check['content']})

        elif layer_check < layer:
            break




    #json_img.insert(count_number_layer, {'type': 'nothing'})


    #printf('\n\n')
    canvas_dict,count_number= {},0
    for per_json_img in json_img_processed:               #处理每个模块之间的关系
        printf(per_json_img)
        count_number+=1

        match per_json_img['type']:
            case 'text':
                Text=TextModule(layer_img_info, per_json_img)
                canvas_dict[count_number]= getattr(Text, per_json_img['subtype'])()
            case 'img':
                Image = ImageModule(layer_img_info, per_json_img)
                canvas_dict[count_number] = getattr(Image, per_json_img['subtype'])()
            case 'avatar':
                Image = AvatarModule(layer_img_info, per_json_img)
                canvas_dict[count_number] = getattr(Image, per_json_img['subtype'])()
            case 'games':
                Image = GamesModule(layer_img_info, per_json_img)
                canvas_dict[count_number] = getattr(Image, per_json_img['subtype'])()
            case 'layer_processed':
                canvas_dict[count_number] = per_json_img['content']
            case _:
                pass
    layer_img_canvas=layer_img_info.paste_img(canvas_dict)
    #layer_img_canvas.show()
    upshift,downshift=0,0
    return {'layer_img_canvas':layer_img_canvas,
            'content':{'canvas':layer_img_canvas, 'canvas_bottom': layer_img_canvas.height - layer_img_info.padding_up_common * 2  ,
                       'upshift':layer_img_info.padding_up_common,'downshift':downshift}}


async def deal_img(json_img): #此函数将逐个解析json文件中的每个字典并与之对应的类相结合
    printf_check(json_img)
    printf('开始处理图片')
    basic_json_set= json_img.copy()
    for per_json_img in basic_json_set:               #优先将图片的基本信息创建好，以免出错
        if 'basic_set' in per_json_img['type']:
            basic_img_info = basicimgset(per_json_img)
            basic_img = basic_img_info.creatbasicimgnobackdrop()
            break


    layer_img_canvas=(await layer_deal(basic_img_info,json_img))['layer_img_canvas']

    basic_img=basic_img_info.combine_layer_basic(basic_img,layer_img_canvas)
    #basic_img.show()

    for per_json_img in basic_json_set:               #处理背景相关
        if 'backdrop' in per_json_img['type']:
            backdrop_class=Backdrop(basic_img_info, per_json_img)
            basic_img=getattr(backdrop_class, per_json_img['subtype'])(basic_img)




    if basic_img_info.is_abs_path_convert is True:
        basic_img_info.img_path_save = get_abs_path(basic_img_info.img_path_save,is_ignore_judge=True)
    img_path = basic_img_info.img_path_save+"/" + random_str() + ".png"
    basic_img.save(img_path, "PNG")
    if basic_img_info.debug is True:
        basic_img.show()

    try:#做好对应资源关闭并释放，以免卡顿
        basic_img.close()
        del basic_img
        gc.collect()
        printf('图片缓存成功释放')
    except:
        printf('绘图资源释放失败，长期可能会导致缓存过大引起卡顿')

    return img_path