from PIL import Image, ImageDraw
from .initialize import initialize_yaml_must_require
from framework_common.manshuo_draw.core.util import *

class LayerSet:
    def __init__(self,basic_img_set,layer_set=1):
        for key, value in vars(basic_img_set).items():#继承父类属性，主要是图片基本设置类
            setattr(self, key, value)

        self.img_width = self.img_width - self.padding_left_common * layer_set * 2

    def paste_img(self,params):
        layer_canvas = Image.new("RGBA", (self.img_width, self.img_height), (103, 195, 243, 255))
        layer_bottom=self.padding_up_common
        #print(params)
        for param in params:
            #print(param,params[param])
            if params[param] is None:continue
            layer_canvas.paste(params[param]['canvas'], (0, int(layer_bottom)), mask=params[param]['canvas'])
            layer_bottom += params[param]['canvas_bottom'] + self.padding_up_layer
        layer_canvas.crop((0, 0, self.img_width, layer_bottom+self.padding_up_common-self.padding_up_layer))
        #layer_canvas.show()
        #layer_canvas.save('data/cache/1.png', "PNG")
        return layer_canvas