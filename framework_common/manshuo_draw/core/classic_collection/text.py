from PIL import Image, ImageDraw, ImageFont, ImageOps,ImageFilter
from .initialize import initialize_yaml_must_require
from framework_common.manshuo_draw.core.util import *

class TextModule:
    def __init__(self,layer_img_set,params):
        for key, value in vars(layer_img_set).items():#继承父类属性，主要是图片基本设置类
            setattr(self, key, value)

        default_keys_values, must_required_keys = initialize_yaml_must_require(params)
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

    def pure_text(self):
        pure_backdrop = Image.new("RGBA", (self.img_width, self.img_height), (0, 0, 0, 0))

        x, y = (self.padding,0)  # 初始位置


        draw = ImageDraw.Draw(pure_backdrop)
        i = 0
        canvas_bottom=0
        # 对文字进行逐个绘制
        text=self.content
        #printf(text[0])
        font = ImageFont.truetype(self.font, self.font_size)
        while i < len(text):  # 遍历每一个字符
            bbox = font.getbbox(text[i])
            char_width = bbox[2] - bbox[0]
            draw.text((x, y), text[i], font=font, fill=self.color)
            x += char_width + self.spacing
            i += 1
            if x+10 > (self.img_width - self.padding*2) and i < len(text):
                char_hight = bbox[3] - bbox[1]
                y += char_hight + self.padding_up
                x=self.padding
        canvas_bottom=y + self.font_size + 1
        pure_text_canvas = pure_backdrop.crop((0,0,self.img_width,canvas_bottom))
        return {'canvas':pure_text_canvas,'canvas_bottom':canvas_bottom}

