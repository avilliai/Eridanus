from PIL import Image, ImageDraw, ImageFilter, ImageOps
from .initialize import initialize_yaml_must_require

class basicimgset:
    def __init__(self, params):
        default_keys_values,must_required_keys=initialize_yaml_must_require(params)
        self.must_required_keys = must_required_keys or []  # 必须的键，如果没有提供就默认是空列表
        self.default_keys_values = default_keys_values or {}  # 默认值字典
        # 检测缺少的必需键
        #print(must_required_keys)
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




    def creatbasicimgnobackdrop(self):
        """
        创建一个同名空白画布并返回。

        """
        # 创建一个指定大小和颜色的画布
        canvas = Image.new("RGBA", (self.img_width, self.img_height), (0, 0, 0, 0))
        return canvas


    def combine_layer_basic(self,basic_img,layer_img_canvas):
        width, height = layer_img_canvas.size
        if height > self.img_height - self.padding_up_common * 2:
            height = self.img_height - self.padding_up_common * 2
            layer_img_canvas = layer_img_canvas.crop((0, 0, width, height))
        # 圆角处理
        if self.is_rounded_corners_front and self.is_rounded_corners_layer:
            mask = Image.new("L", layer_img_canvas.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle((0, 0, width, height), radius=self.rounded_corners_radius, fill=255, outline=255, width=2)
            rounded_image = Image.new("RGBA", layer_img_canvas.size)
            rounded_image.paste(layer_img_canvas, (0, 0), mask=mask)
            layer_img_canvas=rounded_image
        # 阴影处理
        if self.is_shadow_front and self.is_shadow_layer:
            shadow_image = Image.new("RGBA", basic_img.size, (0, 0, 0, 0))  # 初始化透明图层
            shadow_draw = ImageDraw.Draw(shadow_image)
            # 计算阴影矩形的位置
            shadow_rect = [
                self.padding_left_common - self.shadow_offset,  # 左
                self.padding_up_common - self.shadow_offset,  # 上
                self.padding_left_common + width + self.shadow_offset,  # 右
                self.padding_up_common + height + self.shadow_offset  # 下
            ]
            # 绘制阴影（半透明黑色）
            shadow_draw.rectangle(shadow_rect, fill=(0, 0, 0, self.shadow_opacity))
            # 对阴影层应用模糊效果
            shadow_image = shadow_image.filter(ImageFilter.GaussianBlur(self.blur_radius))
            # 将阴影层与底层图像 layer2 合并
            combined_shadow = Image.alpha_composite(basic_img, shadow_image)
            combined_shadow.paste(layer_img_canvas, (self.padding_left_common,self.padding_up_common), mask=layer_img_canvas)
            basic_img = combined_shadow

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

        basic_img.paste(layer_img_canvas, (self.padding_left_common, self.padding_up_common,self.padding_left_common + width,self.padding_up_common + height), mask=layer_img_canvas)
        return basic_img