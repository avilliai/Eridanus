import re
from PIL import Image, ImageDraw, ImageFilter, ImageOps,ImageFont
import platform

def deal_text_with_tag(input_string):
    pattern = r'\[(\w+)\](.*?)\[/\1\]'
    matches = list(re.finditer(pattern, str(input_string), flags=re.DOTALL))
    result = []
    last_end = 0  # 记录上一个匹配结束的位置
    for match in matches:
        start, end = match.span()
        # 处理非标签内容（在上一个匹配结束到当前匹配开始之间的部分）
        if last_end < start:
            non_tag_content = input_string[last_end:start]
            if non_tag_content:
                result.append({'content': non_tag_content,'tag': 'common'})
        # 处理标签内容
        tag = match.group(1)  # 标签名
        content = match.group(2)
        result.append({'content': content, 'tag': tag})
        last_end = end
    # 处理最后的非标签内容（在最后一个标签结束到字符串末尾之间的部分）
    if last_end < len(input_string):
        non_tag_content = input_string[last_end:]
        if non_tag_content:
            result.append({'content': non_tag_content,'tag': 'common'})

    return result


def can_render_character(font, character):
    """
    检测文字是否可以正常绘制
    此处受限于pillow自身的绘制缺陷
    在无法绘制后让另一个模块进行处理
    """
    if character==' ':return True
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
        return False

def color_emoji_maker(text,color,size=40):
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
    font = ImageFont.truetype(font_path, size)
    draw.text((0, 0), text, font=font, fill=color)
    #image.show()
    return image



def basic_img_draw_text(canvas,content,params,box=None,limit_box=None,is_shadow=False):
    """
    #此方法不同于其余绘制方法
    #其余绘制方法仅返回自身绘制画面
    #此方法返回在原画布上绘制好的画面，同时返回的底部长度携带一个标准间距，此举意在简化模组中的叠加操作，请注意甄别
    """

    if box is None: box = (params['padding'], 0)  # 初始位置
    x, y = box
    if limit_box is None:
        x_limit, y_limit = (params['img_width'] - params['padding'] * 2, params['img_height'])  # 初始位置
    else:
        x_limit, y_limit = limit_box
    if content == '' or content is None:
        return {'canvas': canvas, 'canvas_bottom': y}

    content_list = deal_text_with_tag(content)
    #print(content_list)

    # 这一部分检测每行的最大高度
    last_tag,line_height_list,per_max_height = 'Nothing',[],0
    for content in content_list:
        if last_tag != content['tag']:
            last_tag = content['tag']
            try:
                font = ImageFont.truetype(params[f'font_{last_tag}'], params[f'font_{last_tag}_size'])
            except OSError:
                font = ImageFont.load_default()
        i = 0
        # 对文字进行逐个绘制
        text = content['content']
        while i < len(text):  # 遍历每一个字符
            if text[i] == '': continue
            char_width = font.getbbox(text[i])[2] - font.getbbox(text[i])[0]
            if params[f'font_{last_tag}_size'] > per_max_height: per_max_height = params[f'font_{last_tag}_size']
            x += char_width + 1
            i += 1
            if (x + char_width > x_limit and i < len(text)) or text[i - 1] == '\n':
                if x != box[0] + char_width + 1 :
                    x = box[0]
                    line_height_list.append(per_max_height)
                    per_max_height=0
                if x == box[0] + char_width + 1 and text[i - 1] == '\n' :#检测是否在一行最开始换行，若是则修正
                    x -= char_width + 1

    line_height_list.append(params[f'font_common_size'])
    line_height_list.append(params[f'font_common_size'])
    #这一部分开始进行实际绘制
    if box is None: box = (params['padding'], 0)  # 初始位置
    x, y = box
    should_break, last_tag, line_count = False, 'Nothing',0
    #对初始位置进行修正
    y += line_height_list[0] - params[f'font_common_size']

    for content in content_list:
        # 依据字符串处理的字典加载对应的字体
        if last_tag != content['tag']:
            last_tag = content['tag']
            # 设置字体和大小（需要确保字体文件路径正确）
            try:
                font = ImageFont.truetype(params[f'font_{last_tag}'], params[f'font_{last_tag}_size'])
            except OSError:
                font = ImageFont.load_default()
        # 在循环之前进行判断返回，避免过多处理字段
        if y > y_limit - (font.getbbox('的')[3] - font.getbbox('的')[1]):
            return {'canvas': canvas, 'canvas_bottom': y}
        if should_break:  # 检查标志并跳出外层循环
            break

        draw = ImageDraw.Draw(canvas)
        i = 0
        # 对文字进行逐个绘制
        text = content['content']
        while i < len(text):  # 遍历每一个字符
            if text[i] == '': continue
            bbox = font.getbbox(text[i])
            char_width = bbox[2] - bbox[0]
            upshift_font = params[f'font_{last_tag}_size'] - params[f'font_common_size']
            if can_render_character(font, text[i]):
                if is_shadow: draw.text((x + 2, y - upshift_font + 2), text[i], font=font, fill=(148, 148,148))
                draw.text((x, y - upshift_font), text[i], font=font, fill=eval(params[f'font_{last_tag}_color']))
            else:
                try:
                    emoji_img = color_emoji_maker(text[i], eval(params[f'font_{last_tag}_color']))
                    emoji_img = emoji_img.resize((char_width, int(char_width * emoji_img.height / emoji_img.width)))
                    canvas.paste(emoji_img, (int(x), int(y + 3 - upshift_font)), mask=emoji_img)
                except Exception as e:
                    i += 1
                    continue

            x += char_width + 1
            i += 1
            if (x + char_width * 2 > x_limit and i < len(text)) or text[i - 1] == '\n':
                if y > y_limit - (params[f'font_common_size'])  - params['padding_up'] - line_height_list[line_count + 1]:
                    draw.text((x, y), '...', font=font, fill=eval(params[f'font_{last_tag}_color']))
                    should_break = True
                    break
            if (x + char_width > x_limit and i < len(text)) or text[i - 1] == '\n':
                if x != box[0] + char_width + 1 :
                    line_count += 1
                    y += params[f'font_common_size'] + params['padding_up'] + line_height_list[line_count] - params[f'font_common_size']
                    x = box[0]
                if x == box[0] + char_width + 1 and text[i - 1] == '\n' :#检测是否在一行最开始换行，若是则修正
                    x -= char_width + 1
    canvas_bottom = y + params[f'font_common_size'] + 2
    return {'canvas': canvas, 'canvas_bottom': canvas_bottom}


if __name__ == '__main__':
    # 输入字符串
    input_string = "这里是manshuo[title]！这部分是测manshuo！[/title]这manshuo！[des]这里是介绍[/des]这里是manshuo[title]！这部分是测manshuo！[/title]"

    # 调用函数
    output = deal_text_with_tag(input_string)
    for item in output:
        print(item)
    # 输出结果
    print(output)