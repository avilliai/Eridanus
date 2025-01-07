from PIL import Image, ImageDraw, ImageFont, ImageOps,ImageFilter
import os
import textwrap
import re




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

def creat_white_corners(canvas, content_width, content_height,padding_x,current_y,radius=None,type=None):
    shadow_width = 10  # Shadow width
    shadow_color = (255, 255, 255, 80)
    if type is not None: shadow_color = (255, 255, 255, 80)
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
    number_check = 0
    lines = []  # 用于存储最终的每一行
    check_lines=[]
    words = text.split("\n")  # 按换行符分割文本，逐行处理
    if type in (11, 12):
        type_check = True
    else:
        type_check = False

    for line in words:  # 遍历每一行（处理换行符的部分）
        line_check = ""  # 用于拼接当前正在处理的行

        for char in line:  # 遍历每一行的字符，包括空格
            # 获取当前行加上新字符后的宽度
            bbox = font.getbbox(line_check + char)
            text_width = bbox[2] - bbox[0]  # 计算宽度

            if text_width  > max_width:  # 判断加上字符后是否超过最大宽度
                check_lines.append(line_check)
                lines.append(check_lines)  # 将当前行加入结果
                check_lines=[]
                number_check += 1
                if type_check and number_check == 3:  # 如果限制行数为3，直接返回
                    return lines
                line_check = ""  # 清空当前行

            line_check += char  # 将当前字符加入当前行

        if line_check:  # 如果还有剩余内容（最后一行未加入）
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


def handle_context(contents,font,content_width,total_height,padding,type_check,introduce,font_tx,header_height):
    total_height+=header_height + padding +50
    # 处理内容
    processed_contents = []
    image_row = []  # 存储连续图片的队列
    introduce_content=None
    introduce_height=None

    for content in contents:
        if isinstance(content, str) and os.path.splitext(content)[1].lower() in [".jpg", ".png", ".jpeg"]:
            # 处理图片
            img = Image.open(content)
            image_row.append(img)
        elif isinstance(content, str):
            # 处理文字
            if image_row:
                processed_contents.append(image_row)
                image_row = []
            lines = wrap_text(content, font, content_width)
            processed_contents.append(lines)
    if image_row:
        processed_contents.append(image_row)
    # 计算总高度
    check_img=0
    check_text=0
    check_text_height=0
    for content in processed_contents:
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
            elif len(content) == 3:  # 三张图片
                img = content[0]
                new_height = int(((content_width- 2 * padding) // 3 ) * img.height / img.width)
                total_height += new_height + padding
            elif len(content) > 3:  # 三张以上图片
                if len(content)%3 == 0 :
                    len_number=len(content)//3
                else:len_number=len(content)//3+1
                img = content[0]
                new_height = int(((content_width- 2 * padding) // 3 ) * img.height / img.width)*len_number
                total_height += new_height + padding * len_number
                #print(int(((content_width- 2 * padding) // 3 ) * img.height / img.width),new_height,padding * len_number,len_number)
                #print(int((((content_width - 2 * padding) // 3)) * img.height / img.width),total_height)
        elif isinstance(content, list):  # 文字
            check_text=1
            check_img = 0
            if len(content) == 1:  # 单张图片
                line_height = font.getbbox("A")[3]
                total_height += line_height + padding
                check_text_height+= line_height + padding
            else:
                line_height = font.getbbox("A")[3]
                total_height += len(content) * line_height + padding + padding*(len(content)-1)*0.8
                check_text_height+= len(content) * line_height + padding + padding*(len(content)-1)*0.8


    if check_img == 0 and check_text==1 :#如果是图片结尾则不加长，若是文字结尾则加长一小段
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
               introduce_contentm,introduce_content,font_tx_introduce,current_y_set=None,total_height=None):
    draw = ImageDraw.Draw(canvas)
    # 显示头像和名字
    if current_y_set is None:
        current_y_set=0
    current_y = padding + 30 + current_y_set

    if current_y_set is not None and total_height is not None:
        #print(total_height,current_y_set)
        white_dy_img = total_height - current_y_set-padding*3
        canvas=creat_white_corners(canvas, content_width+padding_x,int(white_dy_img),padding_x, current_y-padding)

        gradient_layer = create_gradient_background((int(content_width+padding_x), int(white_dy_img)),
                                                    color1=(235, 239, 253), color2=(236, 255, 252))
        gradient_layer = add_rounded_corners(gradient_layer, radius=20)
        canvas = add_shaow_image_new(canvas, padding, content_width+padding_x, total_height,padding_x,current_y-padding)
        creat_white_corners(canvas, int(content_width+padding_x), int(white_dy_img), padding_x, current_y-padding)
        canvas.paste(gradient_layer, (int(padding_x), int(current_y-padding)), gradient_layer)


    if avatar_path:
        draw = ImageDraw.Draw(canvas)
        avatar_size = 100
        padding_x_tx=int(padding_x_text+20)
        print(avatar_path)
        avatar = Image.open(avatar_path).convert("RGBA")
        avatar.thumbnail((avatar_size, avatar_size))
        creat_white_corners(canvas, avatar_size, avatar_size, padding_x_tx, current_y, radius=min(avatar.size) // 2)
        avatar = add_rounded_corners(avatar, radius=min(avatar.size) // 2)
        canvas.paste(avatar, (int(padding_x_tx), int(current_y)), avatar)
        name_x = padding_x_tx + avatar_size + padding_x_text-20
        draw.text((name_x, current_y-30 + (avatar_size - font_size) // 2), name, fill=(251,114,153), font=font_tx_pil)
        if Time is not None:
            draw.text((name_x, current_y+20 + (avatar_size - font_size) // 2), Time, fill=(148,148,148), font=font_tx)

    current_y += header_height
    img_check=False
    # 绘制内容
    for content in processed_contents:

        if isinstance(content, list) and isinstance(content[0], Image.Image):
            img_check=True
            if len(content) == 1:  # 单张图片
                img = content[0]
                img = img.resize((content_width, int(content_width * img.height / img.width)))
                img = add_rounded_corners(img, radius=20)
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
            elif len(content) == 3:  # 三张图片
                new_width = ((content_width- 2 * padding) // 3)
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
            elif len(content) > 3:  # 三张以上图片
                new_width = ((content_width- 2 * padding) // 3)
                x_offset = padding_x_text
                check=0
                check_flag=1
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
                    if check==3:
                        check=0
                        check_flag+=1
                        current_y += img.height + padding
                        x_offset = padding_x_text
                current_y =check_y+img.height + padding
        elif isinstance(content, list):  # 文字

            if type_check  is True and introduce is not None:
                padding_x_check=padding_x_text+padding*0.3
            else:padding_x_check=padding_x_text

            draw = ImageDraw.Draw(canvas)
            check_number=0
            if len(content) == 1:
                line = content[0][0]
                pattern = r'#.*?#'
                matches = re.findall(pattern, line)
                if 'tag:' in line:
                    line = line.split("tag:")[1]
                    draw.text((padding_x_check, current_y), line, fill=(9, 132, 204), font=font_tx)
                elif matches:
                    draw.text((padding_x_check, current_y), line, fill=(9, 132, 204), font=font_tx)
                else:
                    draw.text((padding_x_check, current_y), line, fill='black', font=font_tx)
                current_y += font_tx.getbbox("A")[3] +padding
            else:
                for line in content:
                    line = line[0]
                    pattern = r'#.*?#'
                    matches = re.findall(pattern, line)
                    #print(line)
                    check_number+=1
                    if 'tag:' in line:
                        line = line.split("tag:")[1]
                        draw.text((padding_x_check, current_y), line, fill=(9, 132, 204), font=font_tx)
                    elif matches:
                        draw.text((padding_x_check, current_y), line, fill=(9, 132, 204), font=font_tx)
                    else:
                        draw.text((padding_x_check, current_y), line, fill='black', font=font_tx)
                    current_y += font_tx.getbbox("A")[3] + padding * 0.8
                current_y += padding* 0.2

            #绘制简介
            if type_check is True and introduce is not None and img_check == True and introduce_height is not None:
                current_y -= padding * 0.2
                #current_y += padding * 0.6
                print(f'introduce_height: {introduce_height}')
                print(f'introduce_content: {introduce_content}')
                for line in introduce_content:
                    draw.text((padding_x_check, current_y), f'{line[0]}', fill=(148,148,148), font=font_tx_introduce)
                    line_height = font_tx.getbbox("A")[3]
                    current_y += line_height + padding * 0.6
    return canvas,current_y


def draw_adaptive_graphic_and_textual(contents, canvas_width=1000, padding=25, font_size=30,
                         avatar_path=None, name=None,Time=None,type=None,introduce=None,title=None,
                         contents_dy=None,orig_avatar_path=None, orig_name=None,orig_Time=None,
                         filepath=None):
    """
    图像绘制
    type类型说明：
    不传入则是默认从上往下的自适应排版
    11：视频解析绘图
    12：Opus图文解析绘图
    13：动态投稿视频绘图

    :return:
    """
    # 准备字体
    if filepath is None:
        filepath=f'data/'
    #print(filepath)
    output_path=f'{filepath}result.png'
    if avatar_path is None:
        avatar_path = f"{filepath}touxiang.png"
    if orig_avatar_path is None:
        orig_avatar_path = f"{filepath}orig_touxiang.png"
    try:
        font = ImageFont.truetype(f"{filepath}LXGWWenKai-Bold.ttf", font_size)  # 替换为本地字体路径
        font_tx = ImageFont.truetype(f"{filepath}LXGWWenKai-Bold.ttf", font_size)  # 替换为本地字体路径
        font_tx_introduce = ImageFont.truetype(f"{filepath}LXGWWenKai-Bold.ttf", font_size-5)  # 替换为本地字体路径
        font_tx_pil = ImageFont.truetype(f"{filepath}LXGWWenKai-Bold.ttf", font_size+10)  # 替换为本地字体路径
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
    if type in {11,12,13}:type_check=True

    # 文本自动换行

    (processed_contents,introduce_content,introduce_height,total_height) = handle_context(contents,font, content_width,
                                total_height, padding, type_check, introduce, font_tx,header_height)
    #print(processed_contents,introduce_content,introduce_height,total_height)
    if type == 14:
        type_check = True
        (orig_processed_contents, orig_introduce_content,
         orig_introduce_height, total_height) = handle_context(contents_dy,font, content_width- padding_x,
                                                total_height, padding,
                                                type_check, introduce,font_tx,header_height)

        #print(orig_processed_contents, orig_introduce_content,orig_introduce_height, total_height)

    # 创建画布
    total_height = int(total_height)
    canvas = create_gradient_background((canvas_width, total_height), color1=(191, 202, 255), color2=(185, 246, 236))
    draw = ImageDraw.Draw(canvas)

    gradient_layer = create_gradient_background((canvas_width - 2 * padding, total_height - 2 * padding),
                                                color1=(235, 239, 253), color2=(236, 255, 252))
    gradient_layer = add_rounded_corners(gradient_layer, radius=20)
    canvas = add_shaow_image(canvas, padding, canvas_width, total_height)
    creat_white_corners(canvas, canvas_width - 2 * padding, total_height - 2 * padding, padding, padding)
    canvas.paste(gradient_layer, (padding, padding), gradient_layer)
    draw = ImageDraw.Draw(canvas)

    canvas,current_y=handle_img(canvas, padding, padding_x,padding_x, avatar_path, font_size, name, Time, header_height,
                   processed_contents, content_width, introduce, type_check, font_tx, font_tx_pil, introduce_height,
                   introduce_content, introduce_content, font_tx_introduce)

    if type == 14:
        current_y_set=current_y
        type_check = True
        canvas ,current_y= handle_img(canvas, padding, padding_x, padding_x +20 ,orig_avatar_path, font_size, orig_name, orig_Time, header_height,
                            orig_processed_contents, content_width - padding_x, introduce, type_check, font_tx, font_tx_pil,
                            orig_introduce_height,orig_introduce_content, orig_introduce_content, font_tx_introduce,current_y,
                            total_height)


    # 保存图片
    canvas.save(output_path)
    #canvas.show()
    return output_path
    #print(f"图片已保存到 {output_path}")



if __name__ == "__main__":
    # 示例内容
    contents = [
        "枫与岚识别：B站:",
        "我不接受这样的全剧终啊啊！2024年10月新番完结吐槽！【泛式】",
        'cover.png',
        '简介：',
        '这结局我急了这结局我急了这结局我急了这结局我急了我急了我急了我急了',
        "image1.jpg",  # 假设是图片路径
        "image2.jpg",  # 假设是图片路径
        "image3.jpg",  # 假设是图片路径
        "image4.jpg",  # 假设是图片路径
        "这是第二段文字",
        "image5.jpg",  # 假设是图片路径
        "这是最后一段文字"
    ]


    # 示例内容
    contents = [
        "这是第一段文字，非常长的话会自动换行，这里是一个测试。这是第一段文字，非常长的话会自动换行，这里是一个测试。这是第一段文字，非常长的话会自动换行，这里是一个测试。这是第一段文字，非常长的话会自动换行，这里是一个测试。",
        "tag:#ARCAEA##Phigros##manshuo#",
        "image5.jpg",
        "这是最后一段文字。",
        "image3.jpg", "image4.jpg",
        "这是最后一段文字。",
        "image3.jpg", "image4.jpg","image4.jpg",
        "这是第二段文字，继续测试文本换行功能。",
        "image2.jpg", "image1.jpg", "image3.jpg",
        "image2.jpg",
        "这是最后一段文字。",
        "image3.jpg", "image4.jpg", "image4.jpg",
        "image3.jpg", "image4.jpg", "image4.jpg",
        "image3.jpg", "image4.jpg",
        "这是最后一段文字。",
        "image3.jpg", "image4.jpg", "image4.jpg",
        "image3.jpg", "image4.jpg", "image4.jpg",
        "image3.jpg", "image4.jpg", "image4.jpg",
        "image3.jpg", "image4.jpg", "image4.jpg",
    ]

    contents = [
        "这是第一段文字，非常长的话会自动",
        "tag:#ARCAEA##Phigros##manshuo#",
        "image5.jpg",
        "这是最后一段文字。",
        "image3.jpg", "image4.jpg",
        "这是最后一段文字。",
        "image3.jpg", "image4.jpg","image4.jpg",
        "这是第二段文字，继续测试文本换行功能。",
        "image2.jpg", "image1.jpg", "image3.jpg",
        "image2.jpg",
        "这是最后一段文字。",
        "image3.jpg", "image4.jpg", "image4.jpg",
        "image3.jpg", "image4.jpg", "image4.jpg",
        "image3.jpg", "image4.jpg",
        "这是最后一段文字。",
        "image3.jpg", "image4.jpg", "image4.jpg",
        "image3.jpg", "image4.jpg", "image4.jpg",
        "image3.jpg", "image4.jpg", "image4.jpg",
        "image3.jpg", "image4.jpg",
    ]
    # 调用函数
    #draw_vertical_layout(contents, name="manshuo",Time='"2025年01月03日 17:00"')

    contents = [
        '咕咕，小鸽子们好！我们将于1月10日晚上8点在Pigeon Bar进行迎新春直播杂谈会——我们会在其中提及全新的游戏内容，当然还有全新的神秘周边首次亮相！\n周五，一起在直播间迎接新春吧~\n',
        "tag:#ARCAEA##Phigros##manshuo#",
        "phigros.jpg",
    ]

    contents = [
        '咕咕，小鸽子们好！我们将于1月10日晚上8点在Pigeon Bar进行迎新春直播杂谈会——我们会在其中提及全新的游戏内容，当然还有全新的神秘周边首次亮相！\n周五，一起在直播间迎接新春吧~\n',
        "tag:#ARCAEA##Phigros##manshuo#",
        "这是第一段文字，非常长的话会自动",
        "tag:#ARCAEA##Phigros##manshuo#",
        "image5.jpg",
        "这是最后一段文字。",
        "image3.jpg", "image4.jpg","image2.jpg",
        "这是第二段文字，继续测试文本换行功能。",
        "image2.jpg", "image1.jpg", "image3.jpg",
        "image2.jpg","image2.jpg","image2.jpg",

    ]
    contents = ['这是一条测试文本\n[保卫萝卜_哇]@酒香亦怕巷子深 \n就测试，不用管\n谢谢']
    contents_dy = ['data/orig_cover.png','【逆转裁判】烦死了身边一帮low货']

    draw_adaptive_graphic_and_textual(contents, name="Phigros",Time='"2025年01月03日 17:00"',type=14,introduce='ooc致歉',
                                      contents_dy=contents_dy,orig_avatar_path=None, orig_name="漫朔",orig_Time='"2025年01月03日 17:00"')
