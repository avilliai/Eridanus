from PIL import Image, ImageDraw, ImageFont, ImageOps,ImageFilter
from .initialize import initialize_yaml_must_require
from framework_common.manshuo_draw.core.util import *
import os
import base64
from io import BytesIO
from datetime import datetime
import calendar

class GamesModule:
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
        if self.img:
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


    def LuRecordMake(self):
        pure_backdrop = Image.new("RGBA", (self.img_width, self.img_height), (0, 0, 0, 0))
        new_width = (((self.img_width - self.padding*2 ) - (self.number_per_row - 1) * self.padding_with) // self.number_per_row)
        per_number_count,number_count,upshift,downshift,current_y,x_offset,max_height = 0,0,0,0,0,self.padding,0
        #若有描边，则将初始粘贴位置增加一个描边宽度
        if self.is_stroke_front and self.is_stroke_img:current_y += self.stroke_img_width / 2
        if self.is_shadow_front and self.is_shadow_img:upshift+=self.shadow_offset_img*2

        #构建图像阵列
        self.processed_img=[]

        first_day_of_week = datetime(datetime.now().year, datetime.now().month, 1).weekday() + 1
        if first_day_of_week == 7: first_day_of_week=0
        x_offset += first_day_of_week * (new_width + self.padding_with)
        _, days_total = calendar.monthrange(datetime.now().year, datetime.now().month)
        background_make=process_img_download(self.background,self.is_abs_path_convert)[0]
        background_make_L = Image.new("RGBA", background_make.size, (255,255,255,255))
        background_make_L.putalpha(background_make.convert('L'))
        for i in range(days_total):
            if f'{i}' in self.content :
                if self.content[f'{i}']['type'] == 'lu':self.processed_img.append(background_make)
                elif self.content[f'{i}']['type'] == 'nolu': self.processed_img.append(background_make)
            else:self.processed_img.append(background_make_L)

        #对每个图片进行单独处理
        for img in self.processed_img:
            img = img.resize((new_width, int(new_width * img.height / img.width)))
            if f'{number_count}' in self.content :
                if self.content[f'{number_count}']['type'] == 'lu' and int(self.content[f'{number_count}']['times']) not in {0,1}:
                    img = basic_img_draw_text(img, f"[lu]×{self.content[f'{number_count}']['times']}[/lu]", self.__dict__, box=( self.padding,img.height - self.font_lu_size - self.padding),)['canvas']
                elif self.content[f'{number_count}']['type'] == 'nolu':
                    img = basic_img_draw_text(img, f"[date]戒🦌[/date]", self.__dict__, box=( self.padding,img.height - self.font_date_size - self.padding),)['canvas']
            else:
                img = basic_img_draw_text(img, f"[date]{number_count+1}[/date]", self.__dict__, box=(self.padding *1.6,img.height - self.font_date_size - self.padding),)['canvas']


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