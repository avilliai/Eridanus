from PIL import Image, ImageDraw
from .initialize import initialize_yaml_must_require
from framework_common.manshuo_draw.core.util import *
class Backdrop:
    def __init__(self,basic_img_set,params):
        for key, value in vars(basic_img_set).items():#继承父类属性，主要是图片基本设置类
            setattr(self, key, value)

        default_keys_values, must_required_keys = initialize_yaml_must_require(params)
        self.must_required_keys = must_required_keys or []  # 必须的键，如果没有提供就默认是空列表
        self.default_keys_values = default_keys_values or {}  # 默认值字典
        # 检测缺少的必需键
        missing_keys = [key for key in self.must_required_keys if key not in params]
        if missing_keys:
            raise ValueError(f"初始化中缺少必需的键: {missing_keys}，请检查传入的数据是否有误")
        # 设置默认值
        for key, value in self.default_keys_values.items():
            setattr(self, key, value)
        # 将字典中的键值转化为类的属性
        for key, value in params.items():
            setattr(self, key, value)
        #是否获取其绝对路径
        if self.is_abs_path_convert is True:
            for key, value in vars(self).items():
                setattr(self, key, get_abs_path(value))

    def one_color(self,basic_img):
        canvas = Image.new("RGBA", (basic_img.width, basic_img.height), eval(self.color))
        canvas.paste(basic_img, (0, 0), mask=basic_img)
        return canvas

    def no_color(self,basic_img):
        canvas = Image.new("RGBA", (basic_img.width, basic_img.height), (0, 0, 0, 0))
        canvas.paste(basic_img, (0, 0), mask=basic_img)
        return canvas

    def gradient(self,basic_img):
        width, height = basic_img.size
        color1=eval(self.left_color)
        color2 = eval(self.right_color)
        gradient = Image.new("RGB", (width, height), color1)  # 创建初始图像
        draw = gradient.load()  # 加载像素点

        # 遍历每个像素，计算其颜色
        for y in range(height):
            for x in range(width):
                # 计算渐变比例
                t = (x / (width - 1) + y / (height - 1)) / 2  # 综合 x 和 y 的比例
                r = int(color1[0] * (1 - t) + color2[0] * t)
                g = int(color1[1] * (1 - t) + color2[1] * t)
                b = int(color1[2] * (1 - t) + color2[2] * t)
                draw[x, y] = (r, g, b)

        gradient.paste(basic_img, (0, 0), mask=basic_img)
        return gradient