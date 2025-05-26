from PIL import Image, ImageDraw, ImageFont, ImageOps,ImageFilter
from .initialize import initialize_yaml_must_require
from framework_common.manshuo_draw.core.util import *
import os
import base64
from io import BytesIO

class ImageModule:
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

        #接下来是对图片进行处理，将其全部转化为pillow的img对象，方便后续处理
        self.processed_img = []
        for content in self.img:
            if isinstance(content, str) and os.path.splitext(content)[1].lower() in [".jpg", ".png", ".jpeg", '.webp']: #若图片为本地文件，则转化为img对象
                self.processed_img.append(Image.open(content))
            elif isinstance(content, str) and content.startswith("http"):
                img_path=download_img(content, self.img_path_save + "/" + random_str() + ".png")
                self.processed_img.append(Image.open(img_path))

            else:#最后判断是否为base64，若不是，则不添加本次图像
                try:
                    self.processed_img.append(Image.open(BytesIO(base64.b64decode(content))))
                except :
                    pass


    def common(self):
        pure_backdrop = Image.new("RGBA", (self.img_width, self.img_height), (0, 0, 0, 0))

        if self.number_per_row == 'default' :
            if len(self.processed_img) == 1:
                self.number_per_row=1
                self.is_crop = False
            elif len(self.processed_img) in [2,4] : self.number_per_row=2
            else: self.number_per_row=3

        new_width = (((self.img_width - self.padding*2 ) - (self.number_per_row - 1) * self.padding_with) // self.number_per_row)
        x_offset = self.padding
        current_y= 0
        number_count = 0
        for img in self.processed_img:
            number_count+=1
            img = img.resize((new_width, int(new_width * img.height / img.width)))

            #img = add_rounded_corners(img, radius=20)
            #creat_white_corners(canvas, new_width, int(new_width * img.height / img.width), x_offset, current_y)

            # 检查透明通道
            if img.mode == "RGBA":pure_backdrop.paste(img, (int(x_offset), int(current_y)), img.split()[3])
            else:pure_backdrop.paste(img, (int(x_offset), int(current_y)))
            x_offset += new_width + self.padding_with
            if number_count == self.number_per_row:
                number_count = 0
                current_y += img.height + self.padding_with
        if number_count != 0:
            current_y  +=  new_width * img.height / img.width

        return {'canvas': pure_backdrop, 'canvas_bottom': current_y - self.padding_with}