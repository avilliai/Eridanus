from PIL import Image,ImageDraw, ImageFilter, ImageOps
from .initialize import initialize_yaml_must_require
from framework_common.manshuo_draw.core.util import *

class LayerSet:
    def __init__(self,basic_img_set,layer_set=1):
        for key, value in vars(basic_img_set).items():#继承父类属性，主要是图片基本设置类
            setattr(self, key, value)
        if not hasattr(self, 'self_basic_class'):  # 如果实例不存在，则创建实例保留
            self.self_basic_class = basic_img_set
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
        # 圆角处理
        if self.is_rounded_corners_front and self.is_rounded_corners_layer:
            mask = Image.new("L", layer_canvas.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle((0, 0, width, height), radius=self.rounded_corners_radius, fill=255, outline=255, width=2)
            rounded_image = Image.new("RGBA", layer_canvas.size)
            rounded_image.paste(layer_canvas, (0, 0), mask=mask)
            layer_canvas=rounded_image
        # 阴影处理
        if self.is_shadow_front and self.is_shadow_layer:
            shadow_image = Image.new("RGBA", basic_img.size, (0, 0, 0, 0))  # 初始化透明图层
            shadow_draw = ImageDraw.Draw(shadow_image)
            # 计算阴影矩形的位置
            shadow_rect = [
                self.padding_left_common - self.shadow_offset_layer,  # 左
                self.padding_up_common - self.shadow_offset_layer,  # 上
                self.padding_left_common + width + self.shadow_offset_layer,  # 右
                self.padding_up_common + height + self.shadow_offset_layer  # 下
            ]
            # 绘制阴影（半透明黑色）
            shadow_draw.rectangle(shadow_rect, fill=(0, 0, 0, self.shadow_opacity_layer))
            # 对阴影层应用模糊效果
            shadow_image = shadow_image.filter(ImageFilter.GaussianBlur(self.blur_radius_layer))
            # 将阴影层与底层图像 layer2 合并
            basic_img = Image.alpha_composite(basic_img, shadow_image)


        # 描边处理
        if self.is_stroke_front and self.is_stroke_layer:
            shadow_image = Image.new('RGBA', (width + self.stroke_layer_width, height + self.stroke_layer_width),(255, 255, 255, 80))
            shadow_blurred = shadow_image.filter(ImageFilter.GaussianBlur(self.stroke_layer_width / 2))
            mask = Image.new('L', shadow_blurred.size, 255)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle([0, 0, shadow_blurred.size[0], shadow_blurred.size[1]],radius=self.stroke_layer_radius, fill=0, outline=255, width=2)
            shadow_blurred = ImageOps.fit(shadow_blurred, mask.size, method=0, bleed=0.0, centering=(0.5, 0.5))
            mask = ImageOps.invert(mask)
            shadow_blurred.putalpha(mask)
            basic_img.paste(shadow_blurred, (int(self.padding_left_common - self.stroke_layer_width / 2), int(self.padding_up_common - self.stroke_layer_width / 2)), shadow_blurred.split()[3])


        basic_img.paste(layer_canvas, (self.padding_left_common, self.padding_up_common, self.padding_left_common + width,self.padding_up_common + height), mask=layer_canvas)
        #basic_img.show()



        #layer_canvas.show()
        #layer_canvas.save('data/cache/1.png', "PNG")
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



