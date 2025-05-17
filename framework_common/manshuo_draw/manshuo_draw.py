from framework_common.manshuo_draw.core.deal_img import *
import asyncio

async def manshuo_draw(json_img, img_path=None):
    #if img_path is not None:json_img['img_path_save']=img_path
    #json_img['img_path_save']=json_img['img_path_save']+'/'+random_str(10)+'.png'
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
        {'type':'basic_set','img_width':1000,'img_height':5000,'padding_common':25,'img_path_save':'data/cache','debug':True},

        {'type': 'backdrop', 'subtype': 'one_color', 'color': '#000000'},

        {'type':'text','subtype':'text','content':'你好，欢迎来到manshuo绘图软件！','font':'default','color':'#000000','size':24},
        {'type':'text','subtype':'text','content':'你好，欢迎来到manshuo绘图软件！这部分是测试内容，请直接忽略，谢谢','font':'default','color':'#000000','size':24,'padding_ahind':25,'padding_with':25},

        {'type': 'img','subtype':'text','img': [],'label':[],'label_color':'','number_per_row':1,'font':'default','color':'#000000','size':24,'padding_ahind':25,'padding_with':25,'is_crop':False},
        {'type': 'img','subtype':'text', 'img': [], 'label': [], 'label_color': '', 'number_per_row': 1, 'font': 'default','color': '#000000', 'size': 24, 'padding_ahind': 25, 'padding_with': 25, 'is_crop': False},
        {'type': 'img','subtype':'text', 'img': [],'label':[],'label_color':'', 'number_per_row': 3,'font':'default','color':'#000000','size':24,'padding_ahind':25,'padding_with':25,'is_crop':False},
        {'type': 'avatar','subtype':'text', 'img': '你好，欢迎来到manshuo绘图软件！','font':'default','padding_ahind':25,'padding_with':25},

        ]

    json_img={
            'type':'draw','software':'manshuo','img_width':1000,'img_height':5000,'padding_common':25,'img_path_save':'data/cache','debug':True,
            'contents':contents
        }

    img_path_set='data/cache'

    loop = asyncio.get_event_loop()
    loop.run_until_complete(manshuo_draw(contents))