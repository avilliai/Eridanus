from PIL import Image, ImageDraw

class basicimgset:
    def __init__(self, params):
        must_required_keys=[]
        default_keys_values={}
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




    def create_canvas(self, width=500, height=500, color=(255, 255, 255)):
        """
        创建一个画布并返回。

        :param width: 画布宽度（默认500像素）
        :param height: 画布高度（默认500像素）
        :param color: 画布背景颜色（默认白色，RGB格式）
        :return: PIL Image 对象
        """
        # 创建一个指定大小和颜色的画布
        canvas = Image.new("RGB", (width, height), color)
        return canvas


