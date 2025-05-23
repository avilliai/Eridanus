from PIL import Image, ImageDraw
from .initialize import initialize_yaml_must_require

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
        # 将字典中的键值转化为类的属性
        for key, value in params.items():
            setattr(self, key, value)
        # 设置默认值
        for key, value in self.default_keys_values.items():
            if not hasattr(self, key):  # 如果属性不存在，则设置默认值
                setattr(self, key, value)

    def one_color(self):
        canvas = Image.new("RGBA", (self.img_width, self.img_height), self.color)
        return canvas

    def no_color(self):
        canvas = Image.new("RGBA", (self.img_width, self.img_height), (0, 0, 0, 0))
        return canvas



