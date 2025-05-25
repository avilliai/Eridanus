from PIL import Image, ImageDraw, ImageFont, ImageOps,ImageFilter
import os
import platform
import re
import inspect
import requests
from urllib.parse import urlparse

def pillow_color_emoji(text, output_file, color):
    system = platform.system()
    image_size = 40
    if system == "Darwin":  # macOS 系统标识
        font_path = "/System/Library/Fonts/Apple Color Emoji.ttc"
    elif system == "Windows":
        font_path = r"C:\Windows\Fonts\seguiemj.ttf"
        image_size = 55
    elif system == "Linux":
        font_path = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
    else:
        raise OSError("暂不支持")
      # 图像大小（宽高相等）
    image = Image.new('RGBA', (image_size, image_size), (255, 255, 255, 0))  # 背景透明
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, 40)
    text_bbox = draw.textbbox((0, 0), text, font=font)  # 获取文本边界框
    text_width = text_bbox[2] - text_bbox[0]  # 计算文本宽度
    text_height = text_bbox[3] - text_bbox[1]  # 计算文本高度
    text_x = (image.width - text_width) // 2
    text_y = (image.height - text_height) // 2
    draw.text((text_x, text_y), text, font=font, fill=color)
    image.save(output_file)
    return output_file

def cario_color_emoji(text,filepath):
    import gi
    gi.require_version("Pango", "1.0")
    gi.require_version("PangoCairo", "1.0")
    from gi.repository import Pango, PangoCairo
    import cairo
    width, height = 50, 50
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    context = cairo.Context(surface)
    context.set_source_rgba(0, 0, 0, 0)
    context.paint()
    layout = PangoCairo.create_layout(context)
    font_description = Pango.FontDescription("Sans 30")  # 使用系统默认 Sans 字体
    layout.set_font_description(font_description)
    layout.set_text(text, -1)
    context.set_source_rgb(0, 0, 0)  # 黑色文本
    context.move_to(0, 0)
    PangoCairo.show_layout(context, layout)
    surface.write_to_png(filepath)
    return filepath

def color_emoji_maker(text,filepath,color):
    try:
        emoji_path=cario_color_emoji(text, filepath)
    except:
        emoji_path=pillow_color_emoji(text, filepath, color)
    return emoji_path


def create_gradient_background(size, color1, color2):

    width, height = size
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




    return gradient

def add_rounded_corners(image, radius):
    """为图片添加圆角效果"""
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, image.width, image.height), radius=radius, fill=255,outline=255,width=2)
    rounded_image = Image.new("RGBA", image.size)
    rounded_image.paste(image, (0, 0), mask=mask)
    return rounded_image

def creat_white_corners(canvas, content_width, content_height,padding_x,current_y,radius=None,type=None,color=None):
    shadow_width = 10  # Shadow width
    shadow_color = (255, 255, 255, 80)
    if type is not None: shadow_color = (255, 255, 255, 80)
    if color is not None: shadow_color = color
    shadow_image = Image.new('RGBA', (content_width + shadow_width,content_height+ shadow_width), shadow_color)
    shadow_blurred = shadow_image.filter(ImageFilter.GaussianBlur(shadow_width / 2))
    shadow_x = int(padding_x - shadow_width / 2)
    shadow_y = int(current_y - shadow_width / 2)
    if radius is None:
        radius = 23
    mask = Image.new('L', shadow_blurred.size, 255)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([0, 0, shadow_blurred.size[0], shadow_blurred.size[1]], radius=radius, fill=0,outline=255,width=2)
    shadow_blurred = ImageOps.fit(shadow_blurred, mask.size, method=0, bleed=0.0, centering=(0.5, 0.5))
    mask = ImageOps.invert(mask)
    shadow_blurred.putalpha(mask)
    canvas.paste(shadow_blurred, (shadow_x, shadow_y), shadow_blurred.split()[3])
    return canvas

def fit_font_size(text, font_path, max_width, starting_font_size=30):
    """动态调整字体大小以适应最大宽度"""
    font_size = starting_font_size
    font = ImageFont.truetype(font_path, font_size)
    while font.getbbox(text)[2] > max_width and font_size > 10:
        font_size -= 1
        font = ImageFont.truetype(font_path, font_size)
    return font

def wrap_text(text, font, max_width,type=None):
    check_type=False
    if text.startswith("title:"):
        text = text.split("title:")[1]
        check_type=True
        start_text='title:'
    number_check = 0
    lines = []  # 用于存储最终的每一行
    check_lines=[]
    words = text.split("\n")  # 按换行符分割文本，逐行处理
    if type in (11, 12):
        type_check = True
    else:
        type_check = False

    for line in words:  # 遍历每一行（处理换行符的部分）
        #print(line)
        if line in ['',' ','	']:continue
        line_check = ""  # 用于拼接当前正在处理的行
        for char in line:  # 遍历每一行的字符，包括空格
            # 获取当前行加上新字符后的宽度
            bbox = font.getbbox(line_check + char)
            text_width = bbox[2] - bbox[0]  # 计算宽度

            if text_width + 20 > max_width:  # 判断加上字符后是否超过最大宽度
                if check_type:
                    line_check= start_text + line_check
                check_lines.append(line_check)
                lines.append(check_lines)  # 将当前行加入结果
                check_lines=[]
                number_check += 1
                if type_check and number_check == 3:  # 如果限制行数为3，直接返回
                    return lines
                line_check = ""  # 清空当前行

            line_check += char  # 将当前字符加入当前行

        if line_check:  # 如果还有剩余内容（最后一行未加入）
            if check_type:
                line_check = start_text + line_check
            check_lines.append(line_check)
            lines.append(check_lines)  # 将当前行加入结果
            check_lines = []
            number_check += 1
            if type_check and number_check == 3:
                return lines
    return lines

def add_shaow_image(canvas,padding,canvas_width,total_height):
    background = canvas.convert("RGBA")
    center_x=int(padding)
    center_y=int(padding)
    img_width=int(canvas_width - 2 * padding)
    img_height=int(total_height - 2 * padding)
    shadow_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))  # 全透明图层
    shadow_draw = ImageDraw.Draw(shadow_layer)
    shadow_offset = 10  # 阴影偏移量
    shadow_rect = [
        center_x - shadow_offset,
        center_y - shadow_offset,
        center_x + img_width + shadow_offset,
        center_y + img_height + shadow_offset,
    ]
    shadow_color = (0, 0, 0, 128)  # 半透明黑色
    shadow_draw.rectangle(shadow_rect, fill=(0, 0, 0, 50))
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(10))
    canvas = Image.alpha_composite(background, shadow_layer)
    return canvas

def add_shaow_image_new(canvas,padding,canvas_width,total_height,x,y):
    background = canvas.convert("RGBA")
    center_x=int(x)
    center_y=int(y)
    img_width=int(canvas_width )
    img_height=int(total_height)
    shadow_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))  # 全透明图层
    shadow_draw = ImageDraw.Draw(shadow_layer)
    shadow_offset = 10  # 阴影偏移量
    shadow_rect = [
        center_x - shadow_offset,
        center_y - shadow_offset,
        center_x + img_width + shadow_offset,
        center_y + img_height + shadow_offset,
    ]
    shadow_color = (0, 0, 0, 128)  # 半透明黑色
    shadow_draw.rectangle(shadow_rect, fill=(0, 0, 0, 50))
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(10))
    canvas = Image.alpha_composite(background, shadow_layer)
    return canvas

def can_render_character(font, character):
    try:
        # 获取字符的掩码
        mask = font.getmask(character)
        # 如果掩码的宽度或高度为 0，说明字符无法绘制
        if mask.size[0] == 0 or mask.size[1] == 0:
            return False
        bbox = font.getbbox(character)
        character_width,character_height = bbox[2] - bbox[0],bbox[3] - bbox[1]
        bbox = font.getbbox("\uFFFD")
        placeholder_width, placeholder_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
        if character_width == placeholder_width and character_height == placeholder_height:
            return False
        return True
    except Exception as e:
        # 如果抛出异常，说明字体不支持该字符
        print(f"Error: {e}")
        return False

def draw_text_step(image, position, text, font, text_color=(0, 0, 0), spacing=None,emoji_list=None,filepath=None):
    """
    在图片上逐个绘制一行文字。

    :param image: Pillow Image 对象
    :param position: 起始位置 (x, y)
    :param text: 要绘制的文字
    :param font: 字体对象 (ImageFont)
    :param text_color: 字体颜色
    :param spacing: 每个字符之间的间距
    """
    if spacing is None:
        spacing=1
    x, y = position  # 初始位置
    flag_emoji=False
    draw = ImageDraw.Draw(image)
    check_emoji_forward=''
    i = 0
    #print(text[0:2])
    #对文字进行逐个绘制
    while i < len(text):                                  # 遍历每一个字符，若遇到表情包则进行下载绘制
        if text[i:i + 2] == '![' and i < len(text) - 1 :
            try:
                char = text[i+2]
                i += 3
                emoji_width = font.getbbox('[1]')[2] - font.getbbox('[1]')[0]
                response = requests.get(emoji_list[int(char)])
                emoji_Path = f"{filepath}/{urlparse(emoji_list[int(char)]).path.split('/')[-1]}.jpg"
                with open(emoji_Path, 'wb') as file:
                    file.write(response.content)
                img = Image.open(emoji_Path).convert("RGBA")
                img = img.resize((emoji_width, int(emoji_width * img.height / img.width)))
                image.paste(img, (int(x), int(y - 5)), img.split()[3])
                x += emoji_width + spacing + 3
            except Exception as e:
                continue
        else:
            # 普通字符输出
            char = text[i]
            i += 1
            if can_render_character(font, char):            # 判断是否可以正常渲染
                bbox = font.getbbox(char)
                char_width = bbox[2] - bbox[0]
                draw.text((x, y), char, font=font, fill=text_color)
            else:                                           # 不能正常渲染则加载默认字体渲染
                bbox = font.getbbox(char)
                char_height = bbox[3] - bbox[1]
                if char_height == 0:
                    bbox = font.getbbox(' ')
                    char_width = bbox[2] - bbox[0]
                    x += char_width + spacing
                    continue
                font_restore = ImageFont.load_default(char_height - 1)
                if can_render_character(font_restore, char):
                    bbox = font_restore.getbbox(char)
                    char_width = bbox[2] - bbox[0]
                    draw.text((x, y), char, font=font_restore, fill=text_color)
                else:
                    try:
                        text_emoji_width = font.getbbox('的')[2] - font.getbbox('的')[0]
                        color_emoji_maker(char,f'{filepath}/{char}.png',text_color)
                        img = Image.open(f'{filepath}/{char}.png').convert("RGBA")
                        img = img.resize((text_emoji_width, int(text_emoji_width * img.height / img.width)))
                        image.paste(img, (int(x), int(y + 3)), img.split()[3])
                        x += text_emoji_width + spacing + 3
                        continue
                    except Exception as e:
                        #continue
                        pass
                        bbox = font.getbbox(' ')
                        char_width = bbox[2] - bbox[0]
            x += char_width + spacing
    return image


def handle_context(contents,font,content_width,total_height,padding,type_check,introduce,font_tx,header_height,
                   type_software=None,height_software=None,avatar_path=None,layer=None,font_tx_pil=None,per_row_pic=3):

    if type_software is not None:
        total_height +=height_software
    if avatar_path is not None:
        if layer is None or layer ==2:
            total_height+=header_height + padding +50
        elif layer == 1:
            total_height+=header_height + padding +50 - 60
    else:
        total_height+= padding +50
    # 处理内容
    processed_contents = []
    image_row = []  # 存储连续图片的队列
    introduce_content=None
    introduce_height=None

    for content in contents:
        if isinstance(content, str) and os.path.splitext(content)[1].lower() in [".jpg", ".png", ".jpeg",'.webp']:
            # 处理图片
            img = Image.open(content)
            image_row.append(img)
        elif isinstance(content, str):
            # 处理文字
            if image_row:
                processed_contents.append(image_row)
                image_row = []
            if content.startswith("title:"):
                lines = wrap_text(content, font_tx_pil, content_width)
            else:
                lines = wrap_text(content, font, content_width)
            if lines != []:
                processed_contents.append(lines)
    if image_row:
        processed_contents.append(image_row)
    # 计算总高度
    check_img=0
    check_text=0
    check_text_height=0
    #print(f'processed_contents:{processed_contents}\ncontent: {content}')
    for content in processed_contents:
        #print(f'content:{content}')
        if isinstance(content, list) and isinstance(content[0], Image.Image):
            check_img=1
            check_text = 0
            if len(content) == 1:  # 单张图片
                img = content[0]
                new_height = int(content_width * img.height / img.width)
                total_height += new_height + padding
            elif len(content) == 2:  # 两张图片
                img = content[0]
                new_height = int(((content_width- padding) // 2 ) * img.height / img.width)
                total_height += new_height + padding
            elif len(content) == per_row_pic:  # 三张图片
                img = content[0]
                new_height = int(((content_width- (per_row_pic-1) * padding) // per_row_pic ) * img.height / img.width)
                total_height += new_height + padding
            elif len(content) == 4:
                img = content[0]
                new_height = int(((content_width - padding) // 2) * img.height / img.width) * 2
                total_height += new_height + padding * 2
            elif len(content) > 4:  # 三张以上图片
                if len(content)%per_row_pic == 0 :
                    len_number=len(content)//per_row_pic
                else:len_number=len(content)//per_row_pic+1
                img = content[0]
                new_height = int(((content_width- (per_row_pic-1) * padding) // per_row_pic ) * img.height / img.width)*len_number
                total_height += new_height + padding * len_number
        elif isinstance(content, list):  # 文字
            check_text=1
            check_img = 0
            if content[0][0].startswith("title:"):
                line_height = font_tx_pil.getbbox("A")[3]
            else:
                line_height = font.getbbox("A")[3]
            total_height += len(content) * line_height + padding + padding * (len(content) - 1) * 0.8
            check_text_height += len(content) * line_height + padding + padding * (len(content) - 1) * 0.8



    if check_img == 0 and check_text==1 and type_check:#如果是图片结尾则不加长，若是文字结尾则加长一小段
        #print('文字加长了')
        total_height+=30

    # 计算简介的高度,如果视频有简介的话
    if type_check and introduce is not None:
        content_width_Dynamic=content_width-padding*0.6
        introduce_content=wrap_text(introduce, font_tx, content_width_Dynamic,type=11)
        #print(introduce_content)
        line_height=font_tx.getbbox("A")[3]
        introduce_height=len(introduce_content) * line_height + padding + padding * (len(introduce_content) - 1) * 0.6
        total_height += introduce_height
        introduce_height+=check_text_height+padding

    return processed_contents,introduce_content,introduce_height,total_height

def handle_img(canvas,padding,padding_x,padding_x_text,avatar_path,font_size,name,Time,header_height,
               processed_contents,content_width,introduce,type_check,font_tx,font_tx_pil,introduce_height,
               introduce_contentm,introduce_content,font_tx_introduce,current_y_set=None,total_height=None,type_software=None,
               color_software=None,layer=None,height_software=None,emoji_list=None,filepath=None,font_tx_title=None,avatar_json=None,per_row_pic=3):

    draw = ImageDraw.Draw(canvas)
    # 显示头像和名字
    if current_y_set is None:
        current_y_set=0
    if type_software is not None:
        current_y_set+=height_software
    current_y = padding + 30 + current_y_set

    if layer is None or layer ==1:
        white_dy_img = total_height - current_y_set-padding*2
        #canvas=creat_white_corners(canvas, content_width+padding*2,int(white_dy_img),padding, current_y-padding)
        gradient_layer = create_gradient_background((int(content_width+2*padding_x-2*padding), int(white_dy_img)),
                                                    color1=(235, 239, 253), color2=(236, 255, 252))
        gradient_layer = add_rounded_corners(gradient_layer, radius=20)
        canvas = add_shaow_image_new(canvas, padding, content_width+2*padding_x-2*padding, total_height,padding,current_y-padding)
        creat_white_corners(canvas, int(content_width+2*padding_x-2*padding), int(white_dy_img), padding, current_y-padding)
        canvas.paste(gradient_layer, (int(padding), int(current_y-padding)), gradient_layer)
    elif layer ==2 :
        #print(total_height,current_y_set)
        white_dy_img = total_height - current_y_set-padding*3
        canvas=creat_white_corners(canvas, content_width+padding_x,int(white_dy_img),padding_x, current_y-padding)
        gradient_layer = create_gradient_background((int(content_width+padding_x), int(white_dy_img)),
                                                    color1=(235, 239, 253), color2=(236, 255, 252))
        gradient_layer = add_rounded_corners(gradient_layer, radius=20)
        canvas = add_shaow_image_new(canvas, padding, content_width+padding_x, total_height,padding_x,current_y-padding)
        creat_white_corners(canvas, int(content_width+padding_x), int(white_dy_img), padding_x, current_y-padding)
        canvas.paste(gradient_layer, (int(padding_x), int(current_y-padding)), gradient_layer)


    if type_software is not None:
        draw = ImageDraw.Draw(canvas)
        bbox = font_tx.getbbox(type_software)
        text_width = bbox[2] - bbox[0]
        x_add=10
        if layer is None or layer == 1:
            creat_white_corners(canvas, text_width+2 * padding+4, int(height_software), padding+x_add, current_y-70-4, radius=10)
            creat_white_corners(canvas, text_width+2 * padding, int(height_software-4),padding+2+x_add,current_y-70-2,radius=10,color=color_software)
            draw.text((padding*2+2+x_add, current_y-70-2), f'{type_software}', fill=(255, 255, 255), font=font_tx)
        elif layer == 2:
            creat_white_corners(canvas, text_width+2 * padding+4, int(height_software), padding_x+x_add, current_y-70-4, radius=10)
            creat_white_corners(canvas, text_width+2 * padding, int(height_software-4),padding_x+2+x_add,current_y-70-2,radius=10,color=color_software)
            draw.text((padding_x+padding+2+x_add, current_y-70-2), f'{type_software}', fill=(255, 255, 255), font=font_tx)

    if avatar_path:
        if layer is None or layer == 2:
            draw = ImageDraw.Draw(canvas)
            avatar_size = 100
            padding_x_tx=int(padding_x_text+20)
            #print(avatar_path)
            avatar = Image.open(avatar_path).convert("RGBA")
            avatar.thumbnail((avatar_size, avatar_size))
            creat_white_corners(canvas, avatar_size, avatar_size, padding_x_tx, current_y, radius=min(avatar.size) // 2)
            avatar = add_rounded_corners(avatar, radius=min(avatar.size) // 2)
            canvas.paste(avatar, (int(padding_x_tx), int(current_y)), avatar)
            name_x = padding_x_tx + avatar_size + padding_x_text-20
            canvas = draw_text_step(canvas, position=(name_x, current_y-30 + (avatar_size - font_size) // 2), text=name, font=font_tx_pil,text_color=(251,114,153))
            if Time is not None:
                canvas = draw_text_step(canvas, position=(name_x, current_y+20 + (avatar_size - font_size) // 2),text=Time, font=font_tx, text_color=(148,148,148))
            if avatar_json is not None:
                if avatar_json['pendant_path']:
                    pendant_size=avatar_size*1.7
                    pendant = Image.open(avatar_json['pendant_path']).convert("RGBA")
                    pendant.thumbnail((pendant_size, pendant_size))
                    canvas.paste(pendant, (int(padding_x_tx-35), int(current_y-30)), pendant)
                if avatar_json['card_path']:
                    if layer == 2:padding_right=400
                    else:padding_right=450
                    card_size = avatar_size
                    card = Image.open(avatar_json['card_path']).convert("RGBA")
                    card.thumbnail((card_size*5, card_size*1.32))
                    width, height = card.size
                    canvas.paste(card, (int(padding_x_tx + padding_right + int(438- width)), int(current_y-15)), card)
                    if avatar_json['card_is_fan']:
                        canvas = draw_text_step(canvas, position=(int(padding_x_tx + padding_right+ 140), int(current_y+35)),text=avatar_json['card_number'], font=font_tx, text_color=avatar_json['card_color'])
            current_y += header_height
        elif layer == 1:
            draw = ImageDraw.Draw(canvas)
            avatar_size = 50
            padding_x_tx = int(padding_x_text + 20)
            # print(avatar_path)
            avatar = Image.open(avatar_path).convert("RGBA")
            avatar.thumbnail((avatar_size, avatar_size))
            creat_white_corners(canvas, avatar_size, avatar_size, padding_x_tx, current_y, radius=min(avatar.size) // 2)
            avatar = add_rounded_corners(avatar, radius=min(avatar.size) // 2)
            canvas.paste(avatar, (int(padding_x_tx), int(current_y)), avatar)
            name_x = padding_x_tx + avatar_size + padding_x_text - 20
            canvas = draw_text_step(canvas, position=(name_x, current_y -10 + (avatar_size - font_size) // 2),text=name, font=font_tx_pil, text_color=(251, 114, 153))
            if Time is not None:
                text_width = font_tx_pil.getbbox(name)[2] - font_tx_pil.getbbox(name)[0]
                canvas = draw_text_step(canvas, position=(name_x +int(text_width) + 30 , current_y -2 + (avatar_size - font_size) // 2),text=Time, font=font_tx, text_color=(148,148,148))
            current_y += header_height - 60



    img_check=False
    # 绘制内容
    for content in processed_contents:

        if isinstance(content, list) and isinstance(content[0], Image.Image):
            img_check=True
            if len(content) == 1:  # 单张图片
                img = content[0]
                img = img.resize((content_width, int(content_width * img.height / img.width)))
                img = add_rounded_corners(img, radius=20)
                #print(f'introduce:{introduce}\nintroduce_height:{introduce_height}')
                if type_check is True and introduce is not None and introduce_height is not None:
                    creat_white_corners(canvas, content_width, int(content_width * img.height / img.width+introduce_height), padding_x_text,current_y)
                else:
                    creat_white_corners(canvas, content_width, int(content_width * img.height / img.width ),padding_x_text,current_y)
                # 检查透明通道
                if img.mode == "RGBA":
                    canvas.paste(img, (int(padding_x_text), int(current_y)), img.split()[3])  # 使用 Alpha 通道作为透明蒙版
                else:
                    canvas.paste(img, (padding_x_text, current_y))  # 无透明通道，直接粘贴
                current_y += img.height + padding
            elif len(content) == 2:  # 两张图片
                new_width = ((content_width- padding) // 2)
                x_offset = padding_x_text
                for img in content:
                    img = img.resize((new_width, int(new_width * img.height / img.width)))
                    img = add_rounded_corners(img, radius=20)
                    creat_white_corners(canvas, new_width, int(new_width * img.height / img.width), x_offset,current_y)
                    # 检查透明通道
                    if img.mode == "RGBA":
                        canvas.paste(img, (int(x_offset), int(current_y)), img.split()[3])
                    else:
                        canvas.paste(img, (int(x_offset), int(current_y)))
                    x_offset += new_width + padding
                current_y += img.height + padding
            elif len(content) == per_row_pic:  # 三张图片
                new_width = ((content_width- (per_row_pic-1) * padding) // per_row_pic)
                x_offset = padding_x_text
                for img in content:
                    img = img.resize((new_width, int(new_width * img.height / img.width)))
                    img = add_rounded_corners(img, radius=20)
                    creat_white_corners(canvas, new_width, int(new_width * img.height / img.width), x_offset, current_y)
                    # 检查透明通道
                    if img.mode == "RGBA":
                        canvas.paste(img, (int(x_offset), int(current_y)), img.split()[3])
                    else:
                        canvas.paste(img, (int(x_offset), int(current_y)))
                    x_offset += new_width + padding
                current_y += img.height + padding

            elif len(content) == 4:  # 四张图片
                new_width = ((content_width - padding) // 2)
                x_offset = padding_x_text
                check = 0
                check_flag = 1
                check_fix_y = 0
                for img in content:
                    check_y = current_y
                    img = img.resize((new_width, int(new_width * img.height / img.width)))
                    img = add_rounded_corners(img, radius=20)
                    creat_white_corners(canvas, new_width, int(new_width * img.height / img.width), x_offset, current_y)
                    # 检查透明通道
                    if img.mode == "RGBA":
                        canvas.paste(img, (int(x_offset), int(current_y)), img.split()[3])
                    else:
                        canvas.paste(img, (int(x_offset), int(current_y)))
                    x_offset += new_width + padding
                    check += 1
                    if img.height >= check_fix_y:
                        check_fix_y = img.height
                    if check == 2:
                        check = 0
                        check_flag += 1
                        current_y += check_fix_y + padding
                        x_offset = padding_x_text
                current_y = check_y + check_fix_y + padding

            elif len(content) > per_row_pic:  # 三张以上图片
                new_width = ((content_width- (per_row_pic-1) * padding) // per_row_pic)
                x_offset = padding_x_text
                check=0
                check_flag=1
                check_fix_y=0
                for img in content:
                    check_y = current_y
                    img = img.resize((new_width, int(new_width * img.height / img.width)))
                    img = add_rounded_corners(img, radius=20)
                    creat_white_corners(canvas, new_width, int(new_width * img.height / img.width), x_offset, current_y)
                    # 检查透明通道
                    if img.mode == "RGBA":
                        canvas.paste(img, (int(x_offset), int(current_y)), img.split()[3])
                    else:
                        canvas.paste(img, (int(x_offset), int(current_y)))
                    x_offset += new_width + padding
                    check+=1
                    if img.height >= check_fix_y:
                        check_fix_y=img.height
                    if check==per_row_pic:
                        check=0
                        check_flag+=1
                        current_y += check_fix_y + padding
                        x_offset = padding_x_text
                current_y =check_y+check_fix_y + padding
        elif isinstance(content, list):  # 文字

            if type_check  is True and introduce is not None:
                padding_x_check=padding_x_text+padding*0.3
            else:padding_x_check=padding_x_text
            #print(content)
            draw = ImageDraw.Draw(canvas)
            check_number=0

            if len(content) == 1:
                line = content[0][0]
                pattern = r'#.*?#'
                matches = re.findall(pattern, line)
                if 'tag:' in line:
                    line = line.split("tag:")[1]
                    canvas = draw_text_step(canvas, position=(padding_x_check, current_y), text=line, font=font_tx,text_color=(9, 132, 204),filepath=filepath,emoji_list=emoji_list)
                    current_y_add=font_tx.getbbox("A")[3]
                elif matches:
                    canvas = draw_text_step(canvas, position=(padding_x_check, current_y), text=line, font=font_tx,text_color=(9, 132, 204),filepath=filepath,emoji_list=emoji_list)
                    current_y_add = font_tx.getbbox("A")[3]
                elif 'title:' in line:
                    line = line.split("title:")[1]
                    canvas = draw_text_step(canvas, position=(padding_x_check, current_y), text=line, font=font_tx_title,text_color=(0, 0, 0), filepath=filepath, emoji_list=emoji_list)
                    current_y_add = font_tx_title.getbbox("A")[3]
                else:
                    canvas = draw_text_step(canvas, position=(padding_x_check, current_y), text=line, font=font_tx,text_color=(0, 0, 0),filepath=filepath,emoji_list=emoji_list)
                    current_y_add = font_tx.getbbox("A")[3]
                current_y += current_y_add +padding
            else:
                for line in content:
                    line = line[0]
                    pattern = r'#.*?#'
                    matches = re.findall(pattern, line)
                    #print(line)
                    check_number+=1
                    if 'tag:' in line:
                        line = line.split("tag:")[1]
                        canvas = draw_text_step(canvas, position=(padding_x_check, current_y), text=line, font=font_tx,text_color=(9, 132, 204),filepath=filepath,emoji_list=emoji_list)
                        current_y_add=font_tx.getbbox("A")[3]
                    elif matches:
                        canvas = draw_text_step(canvas, position=(padding_x_check, current_y), text=line, font=font_tx,text_color=(9, 132, 204),filepath=filepath,emoji_list=emoji_list)
                        current_y_add = font_tx.getbbox("A")[3]
                    elif 'title:' in line:
                        line = line.split("title:")[1]
                        canvas = draw_text_step(canvas, position=(padding_x_check, current_y), text=line, font=font_tx_title,text_color=(0, 0, 0), filepath=filepath, emoji_list=emoji_list)
                        current_y_add = font_tx_title.getbbox("A")[3]
                    else:
                        canvas = draw_text_step(canvas, position=(padding_x_check, current_y), text=line, font=font_tx,text_color=(0, 0, 0),filepath=filepath,emoji_list=emoji_list)
                        current_y_add = font_tx.getbbox("A")[3]
                    current_y += current_y_add + padding * 0.8
                current_y += padding* 0.2

            #绘制简介
            if type_check is True and introduce is not None and img_check == True and introduce_height is not None:
                current_y -= padding * 0.2
                #current_y += padding * 0.6
                #print(f'introduce_height: {introduce_height}')
                #print(f'introduce_content: {introduce_content}')
                for line in introduce_content:
                    draw.text((padding_x_check, current_y), f'{line[0]}', fill=(148,148,148), font=font_tx_introduce)
                    line_height = font_tx.getbbox("A")[3]
                    current_y += line_height + padding * 0.6
    return canvas,current_y


def draw_adaptive_graphic_and_textual(contents, canvas_width=1000, padding=25, font_size=30,
                         avatar_path=None, name=None,Time=None,type=None,introduce=None,title=None,
                         contents_dy=None,orig_avatar_path=None, orig_name=None,orig_Time=None,
                         filepath=None,output_path=None,output_path_name=None,type_software=None,avatar_json=None,
                         color_software=None,orig_type_software=None,emoji_list=None,orig_emoji_list=None,per_row_pic=3):
    """
    图像绘制
    type类型说明：
    不传入则是默认从上往下的自适应排版
    11：视频解析绘图
    12：Opus图文解析绘图
    13：动态投稿视频绘图
    14: 转发动态绘制
    :return:
    """
    # 准备字体
    if filepath is None:
        filepath=f'data/cache/'
    #print(filepath)
    if output_path is None:
        output_path=f'{filepath}result.png'
    if output_path_name is not None:
        output_path=f'{filepath}{output_path_name}.png'
    if avatar_path is None:
        pass
        #avatar_path = f"{filepath}touxiang.png"
    if orig_avatar_path is None:
        orig_avatar_path = f"{filepath}orig_touxiang.png"


    try:
        filepath_fort=f'{os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(draw_adaptive_graphic_and_textual))))}/data/fort/'
        font = ImageFont.truetype(f"{filepath_fort}LXGWWenKai-Regular.ttf", font_size)
        font_tx = ImageFont.truetype(f"{filepath_fort}LXGWWenKai-Regular.ttf", font_size)
        font_tx_introduce = ImageFont.truetype(f"{filepath_fort}LXGWWenKai-Regular.ttf", font_size-5)
        font_tx_pil = ImageFont.truetype(f"{filepath_fort}LXGWWenKai-Regular.ttf", font_size+10)
        font_tx_title= ImageFont.truetype(f"{filepath_fort}LXGWWenKai-Medium.ttf", font_size+10)
    except IOError:
        print("字体 LXGWWenKai-Bold.ttf 未找到，改用默认字体")
        font = ImageFont.load_default()
        font_tx = ImageFont.load_default()
        font_tx_introduce = ImageFont.load_default()
        font_tx_pil = ImageFont.load_default()

    # 头像和名字区域高度
    padding_x=padding+20
    header_height = 150
    content_width = canvas_width - 2 * padding_x  # 内容区域宽度
    total_height = 0  # 累加总高度
    type_check = None
    height_software=40
    if type in {11,12,13}:
        type_check=True
        layer=None
    elif type == 14:
        layer=1
    else:
        layer = None

    # 文本自动换行
    (processed_contents,introduce_content,introduce_height,total_height) = handle_context(contents,font, content_width,
                                total_height, padding, type_check, introduce, font_tx_introduce,header_height,
                                type_software,height_software,avatar_path=avatar_path,layer=layer,font_tx_pil=font_tx_pil,per_row_pic=per_row_pic)
    #print(processed_contents,introduce_content,introduce_height,total_height)
    if type == 14:
        type_check = True
        (orig_processed_contents, orig_introduce_content,
         orig_introduce_height, total_height) = handle_context(contents_dy,font, content_width- padding_x,
                                                total_height, padding,
                                                type_check, introduce,font_tx_introduce,header_height,
                                                orig_type_software,height_software,avatar_path=avatar_path,layer=2,font_tx_pil=font_tx_pil,per_row_pic=per_row_pic)

        #print(orig_processed_contents, orig_introduce_content,orig_introduce_height, total_height)

    # 创建画布
    total_height = int(total_height)
    #print(total_height)
    canvas = create_gradient_background((canvas_width, total_height), color1=(191, 202, 255), color2=(185, 246, 236))
    draw = ImageDraw.Draw(canvas)


    canvas,current_y=handle_img(canvas, padding, padding_x,padding_x, avatar_path, font_size, name, Time, header_height,
                   processed_contents, content_width, introduce, type_check, font_tx, font_tx_pil, introduce_height,
                   introduce_content, introduce_content, font_tx_introduce,total_height=total_height,type_software=type_software,
                   color_software=color_software,height_software=height_software,emoji_list=emoji_list,filepath=filepath,layer=layer
                                ,font_tx_title=font_tx_title,avatar_json=avatar_json,per_row_pic=per_row_pic)

    if type == 14:
        current_y_set=current_y
        type_check = True
        canvas ,current_y= handle_img(canvas, padding, padding_x, padding_x +20 ,orig_avatar_path, font_size, orig_name, orig_Time, header_height,
                            orig_processed_contents, content_width - padding_x, introduce, type_check, font_tx, font_tx_pil,
                            orig_introduce_height,orig_introduce_content, orig_introduce_content, font_tx_introduce,current_y,
                            total_height,layer=2,type_software=orig_type_software,color_software=color_software,height_software=height_software,emoji_list=orig_emoji_list,filepath=filepath
                                      ,font_tx_title=font_tx_title,avatar_json=avatar_json,per_row_pic=per_row_pic)


    # 保存图片
    #canvas.show()
    canvas.save(output_path)
    #print(f"图片已保存到 {output_path}")
    return output_path



if __name__ == "__main__":
    # 示例内容
    contents = ["E:\Others\github/bot\Eridanus\plugins/resource_search_plugin\Link_parsing\data\cache\orig_cover.jpg",
                '【逆转裁判】烦死了身边一帮low货'
                '咕咕，小鸽子们好！我们将于1月10日晚上8点在Pigeon Bar进行迎新春直播杂谈会——我们会在其中提及全新的游戏内容，当然还有全新的神秘周边首次亮相！\n周五，一起在直播间迎接新春吧~\n',
                "tag:#ARCAEA##Phigros##manshuo#",
                ]
    contents_dy = [
                   '【逆转裁判】烦死了身边一帮low货',
                   '官方账号介绍我们啦！🌸',
                   '❣',
                   '敬请期待✨',
                    "E:\Others\github/bot\Eridanus\plugins/resource_search_plugin\Link_parsing\data\cache\orig_cover.jpg",
                    '敬请期待✨',
                   ]

    draw_adaptive_graphic_and_textual(contents, name="Phigros",Time='"2025年01月03日 17:00"',type=14,avatar_path="E:\Others\github/bot\Eridanus\plugins/resource_search_plugin\Link_parsing\data\cache\orig_cover.jpg",
                                      contents_dy=contents_dy,orig_avatar_path="E:\Others\github/bot\Eridanus\plugins/resource_search_plugin\Link_parsing\data\cache\orig_cover.jpg", orig_name="漫朔",orig_Time='"2025年01月03日 17:00"',type_software='BiliBili',
                                      color_software=(251,114,153,80),output_path_name='bilibili_dy')
