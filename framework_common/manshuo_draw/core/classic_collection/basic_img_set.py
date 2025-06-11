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

