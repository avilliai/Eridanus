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
        if not hasattr(self, 'self_basic_class'):  # 如果实例不存在，则创建实例保留
            self.self_basic_class = layer_img_set
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

        if self.number_per_row == 'default' :
            if len(self.processed_img) == 1:
                self.number_per_row=1
                self.is_crop = False
            elif len(self.processed_img) in [2,4] : self.number_per_row=2
            else: self.number_per_row=3

        #接下来处理是否裁剪部分
        if self.is_crop == 'default':
            if self.number_per_row==1: self.is_crop = False
            else: self.is_crop = True

        if self.is_crop is True:
            self.processed_img=self.crop_to_square(self.processed_img)


        new_width = (((self.img_width - self.padding*2 ) - (self.number_per_row - 1) * self.padding_with) // self.number_per_row)
        number_count,upshift,downshift,current_y,x_offset = 0,0,0,0,self.padding
        #若有描边，则将初始粘贴位置增加一个描边宽度
        if self.is_stroke_front and self.is_stroke_img:current_y += self.stroke_img_width / 2
        if self.is_shadow_front and self.is_shadow_img:upshift+=self.shadow_offset*2
        max_proportion=0
        #对每个图片进行单独处理
        for img in self.processed_img:
            proportion = img.height / img.width
            if proportion > max_proportion:max_proportion=proportion
            img = img.resize((new_width, int(new_width * img.height / img.width)))

            #加入label绘制
            img=self.label_process(img,number_count,new_width)

            #对每个图像进行处理
            pure_backdrop,img=self.img_process(pure_backdrop,img,x_offset,current_y,upshift)

            # 检查透明通道
            if img.mode == "RGBA":pure_backdrop.paste(img, (int(x_offset), int(current_y + upshift)), img.split()[3])
            else:pure_backdrop.paste(img, (int(x_offset), int(current_y + upshift)))

            x_offset += new_width + self.padding_with
            number_count += 1
            if number_count == self.number_per_row:
                number_count,x_offset = 0,self.padding
                current_y += img.height + self.padding_with
        if number_count != 0:
            current_y  +=  new_width * max_proportion
        else:
            current_y -= self.padding_with
        #pure_backdrop.show()

        return {'canvas': pure_backdrop, 'canvas_bottom': current_y ,'upshift':upshift,'downshift':downshift}

    def common_with_description(self):
        pure_backdrop = Image.new("RGBA", (self.img_width, self.img_height), (0, 0, 0, 0))
        if self.number_per_row == 'default' :
            if len(self.processed_img) == 1:
                self.number_per_row=1
                self.is_crop = False
            elif len(self.processed_img) in [2,4] : self.number_per_row=2
            else: self.number_per_row=3

        if self.is_crop is True:self.processed_img=self.crop_to_square(self.processed_img)

        new_width = (((self.img_width - self.padding * 2) - (self.number_per_row - 1) * self.padding_with) // self.number_per_row)
        number_count, upshift, downshift, current_y, x_offset = 0, 0, 0, 0, self.padding
        # 若有描边，则将初始粘贴位置增加一个描边宽度
        if self.is_stroke_front and self.is_stroke_img: current_y += self.stroke_img_width / 2
        if self.is_shadow_front and self.is_shadow_img: upshift += self.shadow_offset * 2
        max_proportion = 0
        # 对每个图片进行单独处理
        for img in self.processed_img:
            proportion = img.height / img.width
            if proportion > max_proportion: max_proportion = proportion
            img = img.resize((new_width, int(new_width * img.height / img.width)))

            img_des_canvas = Image.new("RGBA", (img.width, img.height + self.max_des_length), eval(self.description_color))
            font=ImageFont.truetype(self.font, self.font_size)
            font_des = ImageFont.truetype(self.font_des, self.font_des_size)
            des,self.content[number_count]=extract_string(self.content[number_count],'des')

            img_des_canvas.paste(img, (0, 0))
            img_des_canvas_info=self.self_basic_class.basic_img_draw_text(img_des_canvas,self.content[number_count],font,self.font_color,
                                                                     box=(self.padding , img.height + self.padding),padding_up=self.padding,
                                                                     limit_box=(new_width - self.padding,self.max_des_length + img.height))
            img_des_canvas_info = self.self_basic_class.basic_img_draw_text(img_des_canvas_info['canvas'], des, font_des,self.font_des_color,
                                                                            box=(self.padding, img_des_canvas_info['canvas_bottom']),padding_up=self.padding,
                                                                            limit_box=(new_width - self.padding,self.max_des_length + img.height))

            #img_des_canvas_info['canvas'].show()
            des_length = self.max_des_length + img.height
            if int(img_des_canvas_info['canvas_bottom']) < des_length:
                des_length=int(img_des_canvas_info['canvas_bottom'])
            img=img_des_canvas_info['canvas'].crop((0, 0, img.width, des_length))

            #加入label绘制
            img=self.label_process(img,number_count,new_width)

            # 对每个图像进行处理
            pure_backdrop, img = self.img_process(pure_backdrop, img, x_offset, current_y, upshift)

            # 检查透明通道
            if img.mode == "RGBA":
                pure_backdrop.paste(img, (int(x_offset), int(current_y + upshift)), img.split()[3])
            else:
                pure_backdrop.paste(img, (int(x_offset), int(current_y + upshift)))

            x_offset += new_width + self.padding_with
            number_count += 1
            if number_count == self.number_per_row:
                number_count, x_offset = 0, self.padding
                current_y += img.height + self.padding_with
        if number_count != 0:
            current_y += new_width * max_proportion
        else:
            current_y -= self.padding_with

        return {'canvas': pure_backdrop, 'canvas_bottom': current_y, 'upshift': upshift, 'downshift': downshift}

    def img_process(self,pure_backdrop,img,x_offset,current_y,upshift):
        # 圆角处理
        if self.is_rounded_corners_front and self.is_rounded_corners_img:
            mask = Image.new("L", img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle((0, 0, img.width, img.height), radius=self.rounded_img_radius, fill=255, outline=255,
                                   width=2)
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
            shadow_draw.rounded_rectangle(shadow_rect, radius=self.rounded_img_radius,
                                          fill=(0, 0, 0, self.shadow_opacity))
            # 对阴影层应用模糊效果
            shadow_image = shadow_image.filter(ImageFilter.GaussianBlur(self.blur_radius))
            # 将阴影层与底层图像 layer2 合并
            pure_backdrop = Image.alpha_composite(pure_backdrop, shadow_image)

        # 描边处理
        if self.is_stroke_front and self.is_stroke_img:
            shadow_image = Image.new('RGBA', (img.width + self.stroke_img_width, img.height + self.stroke_img_width),
                                     (255, 255, 255, 80))
            shadow_blurred = shadow_image.filter(ImageFilter.GaussianBlur(self.stroke_img_width / 2))
            mask = Image.new('L', shadow_blurred.size, 255)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle([0, 0, shadow_blurred.size[0], shadow_blurred.size[1]],
                                   radius=self.stroke_img_radius, fill=0, outline=255, width=2)
            shadow_blurred = ImageOps.fit(shadow_blurred, mask.size, method=0, bleed=0.0, centering=(0.5, 0.5))
            mask = ImageOps.invert(mask)
            shadow_blurred.putalpha(mask)
            pure_backdrop.paste(shadow_blurred, (int(x_offset - self.stroke_img_width / 2), int(current_y - self.stroke_img_width / 2 + upshift)),shadow_blurred.split()[3])

        return pure_backdrop,img

    def crop_to_square(self,img_list):
        """
        将一个 Pillow 图像对象裁剪为居中的正方形。
        """
        img_processed_list=[]
        for image in img_list:
            width, height = image.size
            # 计算短边的边长，即正方形的边长
            side_length = min(width, height)

            # 计算裁剪区域（左、上、右、下）
            left = (width - side_length) // 2
            top = (height - side_length) // 2
            right = left + side_length
            bottom = top + side_length

            # 裁剪图像
            cropped_image = image.crop((left, top, right, bottom))
            img_processed_list.append(cropped_image)

        return img_processed_list

    def label_process(self,img,number_count,new_width):
        font_label = ImageFont.truetype(self.label_font_path, self.label_font_size)
        label_width, label_height = self.padding * 4, 0
        if number_count  >= len(self.label):
            return img
        if self.label[number_count] == '':
            return img
        label_content = self.label[number_count]

        for per_label_font in label_content:
            label_width += font_label.getbbox(per_label_font)[2] - font_label.getbbox(per_label_font)[0]
            if font_label.getbbox(per_label_font)[3] - font_label.getbbox(per_label_font)[1] > label_height:
                label_height = font_label.getbbox(per_label_font)[3] - font_label.getbbox(per_label_font)[1]
        if label_width > new_width: label_width = new_width
        label_height += self.padding
        label_canvas = Image.new("RGBA", (int(label_width), int(label_height)), eval(self.label_color))

        label_canvas = self.self_basic_class.basic_img_draw_text(label_canvas, label_content,font_label, self.label_font_color,
                                                                        box=(self.padding*1.8, self.padding*0.15),
                                                                        limit_box=(label_width,label_height))['canvas']
        #label_canvas.show()


        if self.is_rounded_corners_front and self.is_rounded_corners_label:
            mask = Image.new("L", label_canvas.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle((0, 0, label_canvas.width, label_canvas.height), radius=self.rounded_label_radius,
                                   fill=255, outline=255, width=2)
            rounded_image = Image.new("RGBA", img.size)
            rounded_image.paste(label_canvas, (0, 0), mask=mask)
            label_canvas = rounded_image
        # 描边处理
        if self.is_stroke_front and self.is_stroke_label:
            shadow_image = Image.new('RGBA',
                                     (label_width + self.stroke_label_width, label_height + self.stroke_label_width),
                                     (255, 255, 255, 255))
            shadow_blurred = shadow_image.filter(ImageFilter.GaussianBlur(self.stroke_label_width / 2))
            mask = Image.new('L', shadow_blurred.size, 255)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle([0, 0, shadow_blurred.size[0], shadow_blurred.size[1]],
                                   radius=self.stroke_label_radius, fill=0, outline=255, width=2)
            shadow_blurred = ImageOps.fit(shadow_blurred, mask.size, method=0, bleed=0.0, centering=(0.5, 0.5))
            mask = ImageOps.invert(mask)
            shadow_blurred.putalpha(mask)
            img.paste(shadow_blurred,
                      (int(img.width - label_width - self.stroke_label_width / 2), - int(self.stroke_label_width / 2)),
                      shadow_blurred.split()[3])

        img.paste(label_canvas, (int(img.width - label_width), 0), mask=label_canvas)
        return img