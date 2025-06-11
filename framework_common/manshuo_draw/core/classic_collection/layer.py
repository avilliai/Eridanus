from PIL import Image,ImageDraw, ImageFilter, ImageOps
from .initialize import initialize_yaml_must_require
from framework_common.manshuo_draw.core.util import *

class LayerSet:
    def __init__(self,basic_img_set,layer_set=1):
        for key, value in vars(basic_img_set).items():#继承父类属性，主要是图片基本设置类
            setattr(self, key, value)
        self.img_width = self.img_width - self.padding_left_common * layer_set * 2

    def paste_img(self,params):
        #layer_canvas = Image.new("RGBA", (self.img_width, self.img_height), (103, 195, 243, 255))
        layer_canvas=self.backdrop_draw(self.backdrop_mode,self.backdrop_color)
        layer_bottom=int(self.padding_up_common)

        for param in params:

            if params[param] is None: continue
            x_offest = (self.img_width - params[param]['canvas'].width) // 2
            layer_canvas.paste(params[param]['canvas'], (x_offest, int(layer_bottom - params[param]['upshift'])), mask=params[param]['canvas'])
            layer_bottom += params[param]['canvas_bottom'] + self.padding_up_layer

        layer_canvas = layer_canvas.crop((0, 0, self.img_width, int(layer_bottom + self.padding_up_common - self.padding_up_layer)))
        #layer_canvas.show()

        width, height = layer_canvas.size
        basic_img = Image.new("RGBA", (width + self.padding_left_common * 2,height+ self.padding_up_common * 2), (0, 0, 0, 0))  # 初始化透明图层
        basic_img = img_process(self.__dict__,basic_img, layer_canvas,self.padding_left_common,self.padding_up_common,0,'layer')
        return basic_img


    def backdrop_draw(self,backdrop_mode,backdrop_color):
        match backdrop_mode:
            case 'no_color':
                layer_canvas = Image.new("RGBA", (self.img_width, self.img_height), (0, 0, 0, 0))
            case 'one_color':
                layer_canvas = Image.new("RGBA", (self.img_width, self.img_height), eval(self.backdrop_color['color1']))
            case 'gradient':
                color1 = eval(self.backdrop_color['color1'])
                color2 = eval(self.backdrop_color['color2'])
                layer_canvas = Image.new("RGB", (self.img_width, self.img_height), color1)  # 创建初始图像
                draw = layer_canvas.load()  # 加载像素点

                # 遍历每个像素，计算其颜色
                for y in range(self.img_height):
                    for x in range(self.img_width):
                        # 计算渐变比例
                        t = (x / (self.img_width - 1) + y / (self.img_height - 1)) / 2  # 综合 x 和 y 的比例
                        r = int(color1[0] * (1 - t) + color2[0] * t)
                        g = int(color1[1] * (1 - t) + color2[1] * t)
                        b = int(color1[2] * (1 - t) + color2[2] * t)
                        draw[x, y] = (r, g, b)
            case _:
                pass
        return layer_canvas



