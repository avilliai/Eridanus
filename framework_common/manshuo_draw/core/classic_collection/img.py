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
        self.processed_img = process_img_download(self.img,self.is_abs_path_convert)
        #判断图片的排版方式
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
        if self.is_crop is True:self.processed_img=crop_to_square(self.processed_img)


    def common(self):
        pure_backdrop = Image.new("RGBA", (self.img_width, self.img_height), (0, 0, 0, 0))
        new_width = (((self.img_width - self.padding*2 ) - (self.number_per_row - 1) * self.padding_with) // self.number_per_row)
        per_number_count,number_count, upshift, downshift, current_y, x_offset, max_height = 0, 0, 0, 0, 0, self.padding, 0
        #若有描边，则将初始粘贴位置增加一个描边宽度
        if self.is_stroke_front and self.is_stroke_img:current_y += self.stroke_img_width / 2
        if self.is_shadow_front and self.is_shadow_img:upshift+=self.shadow_offset_img*2
        #对每个图片进行单独处理
        for img in self.processed_img:
            img = img.resize((new_width, int(new_width * img.height / img.width)))

            #加入label绘制
            img=self.label_process(img,number_count,new_width)

            #对每个图像进行处理
            pure_backdrop = img_process(self.__dict__,pure_backdrop, img, x_offset, current_y, upshift)


            if img.height > max_height: max_height = img.height
            x_offset += new_width + self.padding_with
            per_number_count += 1
            number_count += 1
            if per_number_count == self.number_per_row:
                current_y += max_height + self.padding_with
                per_number_count, x_offset, max_height= 0, self.padding,0
        if per_number_count != 0:
            current_y  +=  max_height
        else:
            current_y -= self.padding_with
        #pure_backdrop.show()

        return {'canvas': pure_backdrop, 'canvas_bottom': current_y ,'upshift':upshift,'downshift':downshift}

    def common_with_des(self):
        pure_backdrop = Image.new("RGBA", (self.img_width, self.img_height), (0, 0, 0, 0))
        new_width = (((self.img_width - self.padding * 2) - (self.number_per_row - 1) * self.padding_with) // self.number_per_row)
        per_number_count,number_count, upshift, downshift, current_y, x_offset, max_height = 0, 0, 0, 0, 0, self.padding, 0
        # 若有描边，则将初始粘贴位置增加一个描边宽度
        if self.is_stroke_front and self.is_stroke_img: current_y += self.stroke_img_width / 2
        if self.is_shadow_front and self.is_shadow_img: upshift += self.shadow_offset_img * 2
        # 对每个图片进行单独处理
        for img in self.processed_img:
            img = img.resize((new_width, int(new_width * img.height / img.width)))
            img_des_canvas = Image.new("RGBA", (img.width, img.height + self.max_des_length), eval(self.description_color))
            img_des_canvas.paste(img, (0, 0))
            img_des_canvas_info=basic_img_draw_text(img_des_canvas,self.content[number_count],self.__dict__,
                                                                     box=(self.padding , img.height + self.padding),
                                                                     limit_box=(new_width - self.padding, self.max_des_length + img.height))
            #img_des_canvas_info['canvas'].show()
            des_length = self.max_des_length + img.height
            if int(img_des_canvas_info['canvas_bottom'] + self.padding_up) < des_length:
                des_length=int(img_des_canvas_info['canvas_bottom'] + self.padding_up)
            img=img_des_canvas_info['canvas'].crop((0, 0, img.width, des_length))

            #加入label绘制
            img=self.label_process(img,number_count,new_width)

            # 对每个图像进行处理
            pure_backdrop = img_process(self.__dict__,pure_backdrop, img, x_offset, current_y, upshift)

            if img.height > max_height: max_height = img.height
            x_offset += new_width + self.padding_with
            per_number_count += 1
            number_count += 1
            if per_number_count == self.number_per_row:
                current_y += max_height + self.padding_with
                per_number_count, x_offset, max_height= 0, self.padding,0
        if per_number_count != 0:
            current_y += max_height
        else:
            current_y -= self.padding_with

        return {'canvas': pure_backdrop, 'canvas_bottom': current_y, 'upshift': upshift, 'downshift': downshift}


    def common_with_des_right(self):
        pure_backdrop = Image.new("RGBA", (self.img_width, self.img_height), (0, 0, 0, 0))
        new_width = (((self.img_width - self.padding * 2) - (self.number_per_row - 1) * self.padding_with) // self.number_per_row)
        per_number_count,number_count, upshift, downshift, current_y, x_offset, max_height = 0, 0, 0, 0, 0, self.padding, 0
        # 若有描边，则将初始粘贴位置增加一个描边宽度
        if self.is_stroke_front and self.is_stroke_img: current_y += self.stroke_img_width / 2
        if self.is_shadow_front and self.is_shadow_img: upshift += self.shadow_offset_img * 2
        # 对每个图片进行单独处理
        for img in self.processed_img:
            if img.height/img.width < 9/16:img_width,img_height=int(new_width / 2),int((new_width / 2.5) * img.height / img.width)
            else:img_width,img_height=int(new_width / 2.5),int((new_width / 2.5) * img.height / img.width)
            img = img.resize((img_width, img_height))
            img_des_canvas = Image.new("RGBA", (new_width, img_height),eval(self.description_color))
            img_des_canvas.paste(img, (0, 0))
            img = basic_img_draw_text(img_des_canvas, self.content[number_count], self.__dict__,
                                                      box=(img_width + self.padding,  self.padding),
                                                      limit_box=(new_width - self.padding, img_height))['canvas']
            # 加入label绘制
            img = self.label_process(img, number_count, img_width)

            # 对每个图像进行处理
            pure_backdrop = img_process(self.__dict__, pure_backdrop, img, x_offset, current_y, upshift)

            if img.height > max_height: max_height = img.height
            x_offset += new_width + self.padding_with
            per_number_count += 1
            number_count += 1
            if per_number_count == self.number_per_row:
                current_y += max_height + self.padding_with
                per_number_count, x_offset, max_height = 0, self.padding, 0
        if per_number_count != 0:
            current_y += max_height
        else:
            current_y -= self.padding_with

        return {'canvas': pure_backdrop, 'canvas_bottom': current_y, 'upshift': upshift, 'downshift': downshift}





    def label_process(self,img,number_count,new_width):
        font_label = ImageFont.truetype(self.font_label, self.font_label_size)
        label_width, label_height,upshift = self.padding * 4, self.padding,0
        if number_count  >= len(self.label) or self.label[number_count] == '':
            return img
        label_content = self.label[number_count]
        #计算标签的实际长度
        for per_label_font in label_content:
            label_width += font_label.getbbox(per_label_font)[2] - font_label.getbbox(per_label_font)[0]
            if font_label.getbbox(per_label_font)[3] - font_label.getbbox(per_label_font)[1] > label_height:
                label_height += font_label.getbbox(per_label_font)[3] - font_label.getbbox(per_label_font)[1]
        if label_width > new_width: label_width = new_width
        label_canvas = Image.new("RGBA", (int(label_width), int(label_height)), eval(self.label_color))
        #调用方法绘制文字并判断是否需要描边和圆角
        label_canvas = basic_img_draw_text(label_canvas, f'[label] {label_content} [/label]', self.__dict__,
                                                                        box=(self.padding*1.3, self.padding*0.6),
                                                                        limit_box=(label_width,label_height))['canvas']
        img = img_process(self.__dict__, img, label_canvas, int(new_width - label_width), 0, upshift,'label')
        return img