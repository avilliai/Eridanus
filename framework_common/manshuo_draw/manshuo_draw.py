from framework_common.manshuo_draw.core.deal_img import *
import asyncio

async def manshuo_draw(json_img):
    #json_img=json_check(json_img)   #检查并补正输入的参数
    await deal_img(json_img)


if __name__ == '__main__':

    """
        定义一个json和内容文件，方便后续进行调试维护,并在此处阐明各个标签的用途
    :type:表示该组件的类型，如text表示文字，img表示图片，avatar表示头像
    :content:表示该组件的内容，如文本内容，图片地址，头像地址
    :font:表示字体类型，如default表示默认字体
    :color:表示字体颜色，如#000000表示黑色
    :size:表示字体大小，如24表示24号字体
    :padding_ahind:表示该组件与上一个组件之间的距离
    :padding_with:表示内容与内容之间的距离
    :img:表示图片地址，如https://i.imgur.com/5y9y95L.jpg
    :label:表示图片标签，如['标签1','标签2']
    :label_color:表示标签颜色，如#000000表示黑色
    :number_per_row:表示每行显示的图片数量，如1表示一行显示一个图片
    :is_crop:表示是否裁剪图片，如True表示裁剪图片为一个正方形
    """
    contents=[
        {'type': 'basic_set', 'debug': False,'is_abs_path_convert':True},

        {'type': 'backdrop', 'subtype': 'gradient'},

        {'type': 'avatar', 'subtype': 'common', 'img': ['framework_common/manshuo_draw/data/cache/manshuo.jpg'],'upshift':25,
         'content':[{'name': '漫朔_manshuo', 'time': '2025年 05月27日 20:32'}]
         },
        {'type': 'img', 'subtype': 'common','img': ['framework_common/manshuo_draw/data/cache/manshuo.jpg'],'label':['BiliBili']},
        {'type': 'img', 'subtype': 'common', 'img': ['framework_common/manshuo_draw/data/cache/manshuo.jpg','https://gal.manshuo.ink/usr/uploads/2025/01/1015237503.png'],
         'label': ['BiliBili','manshuo']},

        {'type': 'text', 'subtype': 'common', 'content': ['这里是manshuo！']},

        {'type': 'img', 'subtype': 'common_with_description', 'img': ['framework_common/manshuo_draw/data/cache/manshuo.jpg','framework_common/manshuo_draw/data/cache/manshuo.jpg'],
         'content': ['这里是manshuo！这部分是测manshuo！这manshuo！[des]这里是介绍[/des]','这里是manshuo！这部分是测manshuo！这manshuo！[des]这里是介绍[/des]'] },


        {'type':'text','subtype':'common','content':['这里是manshuo这里是manshuo这里是manshuo这里是manshuo这里是manshuo这里是manshuo这部分是测试内容，请直接忽略，'],'layer':2,},
        {'type': 'img', 'subtype': 'common_with_description', 'img': ['framework_common/manshuo_draw/data/cache/manshuo.jpg','framework_common/manshuo_draw/data/cache/manshuo.jpg'],
         'content': ['这里是manshuo！这部分是测manshuo！这manshuo！[des]这里是介绍[/des]','这里是manshuo！这部分是测manshuo！这manshuo！[des]这里是介绍[/des]'],'layer':2 },

    ]

    contents_not=[

    ]

    img_path_set='data/cache'


    asyncio.run(manshuo_draw(contents))