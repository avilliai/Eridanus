from PIL import Image, ImageDraw, ImageFont, ImageOps,ImageFilter
from .initialize import initialize_yaml_must_require
from framework_common.manshuo_draw.core.util import *
import os
import base64
from io import BytesIO

class AvatarModule:
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

        # 设置字体和大小（需要确保字体文件路径正确）
        try:
            self.name_font = ImageFont.truetype(self.name_font_path, size=self.name_font_size)
            self.time_font = ImageFont.truetype(self.time_font_path, size=self.time_font_size)
        except OSError:
            self.name_font=self.time_font = ImageFont.load_default()  # 如果字体不可用，使用默认字体

        #接下来是对图片进行处理，将其全部转化为pillow的img对象，方便后续处理
        self.processed_img = []
        for content in self.img:
            if isinstance(content, str) and os.path.splitext(content)[1].lower() in [".jpg", ".png", ".jpeg", '.webp'] and not content.startswith("http"): #若图片为本地文件，则转化为img对象
                if self.is_abs_path_convert is True:content=get_abs_path(content)
                self.processed_img.append(Image.open(content))
            elif isinstance(content, str) and content.startswith("http"):
                self.processed_img.append(Image.open(BytesIO(base64.b64decode(download_img_sync(content)))))

            else:#最后判断是否为base64，若不是，则不添加本次图像
                try:
                    self.processed_img.append(Image.open(BytesIO(base64.b64decode(content))))
                except :
                    pass


    def common(self):
        pure_backdrop = Image.new("RGBA", (self.img_width, self.img_height), (0, 0, 0, 0))
        number_count,upshift,downshift,current_y,x_offset = 0,0,0,self.padding_up_bottom,self.padding
        #若有描边，则将初始粘贴位置增加一个描边宽度
        if self.is_stroke_front and self.is_stroke_img:current_y += self.stroke_img_width / 2
        if self.is_shadow_front and self.is_shadow_img:upshift +=self.shadow_offset*2
        new_width=(((self.img_width - self.padding*2 ) - (self.number_per_row - 1) * self.padding_with) // self.number_per_row)
        for img in self.processed_img:
            img.thumbnail((self.avatar_size, self.avatar_size))
            # 圆角处理
            if self.is_rounded_corners_front and self.is_rounded_corners_img:
                mask = Image.new("L", img.size, 0)
                draw = ImageDraw.Draw(mask)
                draw.rounded_rectangle((0, 0, img.width, img.height), radius=self.rounded_img_radius, fill=255, outline=255, width=2)
                rounded_image = Image.new("RGBA", img.size)
                rounded_image.paste(img, (0, 0), mask=mask)
                img = rounded_image

            # 阴影处理
            if self.is_shadow_front and self.is_shadow_img:
                shadow_image = Image.new("RGBA", pure_backdrop.size, (0, 0, 0, 0))  # 初始化透明图层
                shadow_draw = ImageDraw.Draw(shadow_image)
                # 计算阴影矩形的位置
                shadow_rect = [
                    x_offset - self.shadow_offset,  # 左
                    current_y - self.shadow_offset + upshift,  # 上
                    x_offset + img.width + self.shadow_offset,  # 右
                    current_y + img.height + self.shadow_offset + upshift  # 下
                ]
                # 绘制阴影（半透明黑色）
                shadow_draw.rounded_rectangle(shadow_rect, radius=self.rounded_img_radius,fill=(0, 0, 0, self.shadow_opacity))
                # 对阴影层应用模糊效果
                shadow_image = shadow_image.filter(ImageFilter.GaussianBlur(self.blur_radius))
                # 将阴影层与底层图像 layer2 合并
                pure_backdrop = Image.alpha_composite(pure_backdrop, shadow_image)

            # 描边处理
            if self.is_stroke_front and self.is_stroke_img:
                shadow_image = Image.new('RGBA', (img.width + self.stroke_img_width, img.height + self.stroke_img_width),(255, 255, 255, 80))
                shadow_blurred = shadow_image.filter(ImageFilter.GaussianBlur(self.stroke_img_width / 2))
                mask = Image.new('L', shadow_blurred.size, 255)
                draw = ImageDraw.Draw(mask)
                draw.rounded_rectangle([0, 0, shadow_blurred.size[0], shadow_blurred.size[1]],
                                       radius=self.stroke_img_radius, fill=0, outline=255, width=2)
                shadow_blurred = ImageOps.fit(shadow_blurred, mask.size, method=0, bleed=0.0, centering=(0.5, 0.5))
                mask = ImageOps.invert(mask)
                shadow_blurred.putalpha(mask)
                pure_backdrop.paste(shadow_blurred, (int(x_offset - self.stroke_img_width / 2),int(current_y - self.stroke_img_width / 2 + upshift)),shadow_blurred.split()[3])

            # 检查透明通道
            if img.mode == "RGBA":
                pure_backdrop.paste(img, (int(x_offset), int(current_y + upshift)), img.split()[3])
            else:
                pure_backdrop.paste(img, (int(x_offset), int(current_y + upshift)))


            # 绘制名字和时间等其他信息
            draw = ImageDraw.Draw(pure_backdrop)
            text_x_offset=x_offset + self.avatar_size*1.1 + self.padding_with
            text_y_offset=current_y + self.avatar_size//2
            draw.text((text_x_offset , text_y_offset - self.name_font_size ), self.content[number_count]['name'], font=self.name_font, fill=eval(self.name_font_color))
            draw.text((text_x_offset , text_y_offset + self.padding_with ), self.content[number_count]['time'], font=self.time_font, fill=eval(self.time_font_color))
            x_offset += new_width + self.padding_with

            number_count += 1
            if number_count == self.number_per_row:
                number_count,x_offset = 0,self.padding
                current_y += img.height + self.padding_with
        if number_count != 0:
            current_y += new_width * img.height / img.width
        else:
            current_y -= self.padding_with

        upshift+=self.upshift
        return {'canvas': pure_backdrop, 'canvas_bottom': current_y + self.padding_up_bottom - self.upshift ,'upshift':upshift,'downshift':0}




