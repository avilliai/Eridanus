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

        #接下来是对图片进行处理，将其全部转化为pillow的img对象，方便后续处理

        self.processed_img = process_img_download(self.img,self.is_abs_path_convert)

        self.processed_img = crop_to_square(self.processed_img)


    def common(self):
        pure_backdrop = Image.new("RGBA", (self.img_width, self.img_height), (0, 0, 0, 0))
        number_count,upshift,downshift,current_y,x_offset = 0,0,0,self.padding_up_bottom,self.padding
        #若有描边，则将初始粘贴位置增加一个描边宽度
        if self.is_stroke_front and self.is_stroke_img:current_y += self.stroke_img_width / 2
        if self.is_shadow_front and self.is_shadow_img:upshift +=self.shadow_offset*2
        new_width=(((self.img_width - self.padding*2 ) - (self.number_per_row - 1) * self.padding_with) // self.number_per_row)
        self.icon_backdrop_check()
        for img in self.processed_img:
            img.thumbnail((self.avatar_size, self.avatar_size))

            # 对每个图像进行处理
            pure_backdrop = img_process(self.__dict__,pure_backdrop, img, x_offset, current_y, upshift)


            # 绘制名字和时间等其他信息
            draw_content= f"[name]{self.content[number_count]['name']}[/name]\n[time]{self.content[number_count]['time']}[/time]"
            if self.is_name:
                pure_backdrop=basic_img_draw_text(pure_backdrop,draw_content,self.__dict__,
                                                                     box=(x_offset + self.avatar_size*1.1 + self.padding_with, current_y + self.avatar_size//2  - self.font_name_size*1.2),
                                                                     limit_box=(x_offset + new_width  , current_y  + self.avatar_size ),is_shadow=self.is_shadow_font)['canvas']

            x_offset += new_width + self.padding_with

            number_count += 1
            if number_count == self.number_per_row:
                number_count,x_offset = 0,self.padding
                current_y += img.height + self.padding_with
        if number_count != 0:
            current_y += new_width * img.height / img.width
        else:
            current_y -= self.padding_with

        pure_backdrop = icon_process(self.__dict__, pure_backdrop,(self.img_width - self.padding , current_y ))
        pure_backdrop = backdrop_process(self.__dict__,pure_backdrop,(self.img_width, current_y + self.padding_up_bottom))


        upshift+=self.upshift
        return {'canvas': pure_backdrop, 'canvas_bottom': current_y + self.padding_up_bottom - self.upshift ,'upshift':upshift,'downshift':0}



    def icon_backdrop_check(self):
        if self.type_software is None or self.type_software == 'None' or len(self.processed_img) != 1: return
        for content_check in self.software_list:
            if self.type_software == content_check['type'] :
                self.background,self.right_icon = content_check['background'],content_check['right_icon']
                self.font_name_color,self.font_time_color = '(255,255,255)', '(255,255,255)'
                self.is_shadow_font = True