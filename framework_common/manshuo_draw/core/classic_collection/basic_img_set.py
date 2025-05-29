from PIL import Image, ImageDraw, ImageFilter, ImageOps,ImageFont
from .initialize import initialize_yaml_must_require
from framework_common.manshuo_draw.core.util import *

class basicimgset:
    def __init__(self, params):
        default_keys_values,must_required_keys=initialize_yaml_must_require(params)

        self.must_required_keys = must_required_keys or []  # 必须的键，如果没有提供就默认是空列表
        self.default_keys_values = default_keys_values or {}  # 默认值字典
        # 检测缺少的必需键
        missing_keys = [key for key in self.must_required_keys if key not in params]
        if missing_keys:
            raise ValueError(f"初始化中缺少必需的键: {missing_keys}，请检查传入的数据是否有误")
        # 将字典中的键值转化为类的属性
        for key, value in params.items():
            setattr(self, key, value)
        # 设置默认值
        for key, value in self.default_keys_values.items():
            if not hasattr(self, key):  # 如果属性不存在，则设置默认值
                setattr(self, key, value)

        #是否获取其绝对路径
        if self.is_abs_path_convert is True:
            for key, value in vars(self).items():
                setattr(self, key, get_abs_path(value))


    def creatbasicimgnobackdrop(self):
        """创建一个同名空白画布并返回。"""
        # 创建一个指定大小和颜色的画布
        canvas = Image.new("RGBA", (self.img_width, self.img_height), (0, 0, 0, 0))
        return canvas


    def combine_layer_basic(self,basic_img,layer_img_canvas):

        width, height = layer_img_canvas.size
        if height > self.img_height - self.padding_up_common * 2:
            height = self.img_height - self.padding_up_common * 2
            layer_img_canvas = layer_img_canvas.crop((0, 0, width, height))

        basic_img.paste(layer_img_canvas, (0, 0,width,height), mask=layer_img_canvas)



        basic_img=basic_img.crop((0, 0, self.img_width, height))

        return basic_img

    def basic_img_draw_text(self,canvas,content,font,color,box=None,limit_box=None,padding_up=20):
        """
        #此方法不同于其余绘制方法
        #其余绘制方法仅返回自身绘制画面
        #此方法返回在原画布上绘制好的画面，同时返回的底部长度携带一个标准间距，此举意在简化模组中的叠加操作，请注意甄别
        """

        if box is None: x, y = (self.padding,0)  # 初始位置
        else:x, y = box
        if limit_box is None:x_limit, y_limit = (self.img_width - self.padding*2,self.img_height)  # 初始位置
        else:x_limit, y_limit = limit_box
        if content == '' or content is None:
            return {'canvas': canvas, 'canvas_bottom': y}
        if y > y_limit - (font.getbbox('的')[3] - font.getbbox('的')[1]):
            return {'canvas': canvas, 'canvas_bottom': y}
        draw = ImageDraw.Draw(canvas)
        i = 0
        # 对文字进行逐个绘制
        text=content
        while i < len(text):  # 遍历每一个字符
            bbox = font.getbbox(text[i])
            char_width = bbox[2] - bbox[0]
            draw.text((x, y), text[i], font=font, fill=eval(color))
            x += char_width + 1
            i += 1
            if x + char_width*2 > x_limit and i < len(text):
                if y > y_limit - (font.getbbox('的')[3] - font.getbbox('的')[1] )*2 - padding_up :
                    draw.text((x, y), '...', font=font, fill=eval(color))
                    break

            if x+char_width > x_limit and i < len(text):
                y += font.getbbox('的')[3] - font.getbbox('的')[1] + padding_up
                x=box[0]
        bbox = font.getbbox('的')
        canvas_bottom=y + bbox[3] - bbox[1] + padding_up
        return {'canvas':canvas, 'canvas_bottom':canvas_bottom}