from io import BytesIO

import requests
from PIL import Image, ImageFont, ImageDraw

from framework_common.utils.random_str import random_str

texture_path = "run/resource_collector/service/zLibrary/img.png"
def create_book_image(data):
    #print(data)
    # 加载纹理图片并将其拉伸到画布大小
    texture_image = Image.open(texture_path)

    # 加载封面图片
    response = requests.get(data['cover'])
    cover_image = Image.open(BytesIO(response.content))

    # 计算封面缩放尺寸，确保按比例缩放并留边距
    max_cover_width = 300
    max_cover_height = 450
    cover_ratio = min(max_cover_width / cover_image.width, max_cover_height / cover_image.height)
    cover_width = int(cover_image.width * cover_ratio)
    cover_height = int(cover_image.height * cover_ratio)
    cover_resized = cover_image.resize((cover_width, cover_height))

    # 初始化字体，确保支持中文
    font_title = ImageFont.truetype("simhei.ttf", 24)  # 黑体
    font_text = ImageFont.truetype("simhei.ttf", 18)

    # 计算每行显示的字数
    max_chars_per_line = 25

    def split_text_by_line(text, max_chars):
        """将文本按指定字符数分行"""
        lines = [text[i:i + max_chars] for i in range(0, len(text), max_chars)]
        return lines

    def measure_total_height(lines, font):
        """计算所有行的总高度"""
        return sum(font.getbbox(line)[3] + 5 for line in lines)

    # 准备所有文本
    title_lines = split_text_by_line(data['title'], max_chars_per_line)
    author_lines = split_text_by_line(data['author'], max_chars_per_line)
    year_lines = split_text_by_line(str(data['year']), max_chars_per_line)
    description = data['description'].replace('<p>', '').replace('</p>', '').replace('<br>', '')
    description_lines = split_text_by_line(description, max_chars_per_line)

    # 动态计算所需画布高度，添加缓冲空间
    padding = 20
    text_width = 800 - cover_width - 40  # 动态计算文本宽度
    total_text_height = (
            measure_total_height(title_lines, font_text) +
            measure_total_height(author_lines, font_text) +
            measure_total_height(year_lines, font_text) +
            measure_total_height(description_lines, font_text) +
            200  # 添加额外间距
    )
    canvas_height = max(cover_height + 40, total_text_height + 50)  # 额外预留50像素缓冲空间

    # 创建最终画布，并将纹理图拉伸填充
    canvas = Image.new("RGB", (800, canvas_height), (255, 255, 255))  # 初始化画布
    texture_resized = texture_image.resize((800, canvas_height))  # 拉伸纹理图像填满整个画布
    canvas.paste(texture_resized, (0, 0))  # 将拉伸后的纹理图粘贴为背景

    draw = ImageDraw.Draw(canvas)

    def draw_text_lines(draw, x, y, lines, font):
        """按行绘制文本"""
        for line in lines:
            draw.text((x, y), line, font=font, fill="black")
            y += font.getbbox(line)[3] + 5
        return y

    # 绘制封面
    canvas.paste(cover_resized, (20, 20))

    # 绘制文本内容
    x_offset = cover_width + 40
    y_offset = 20

    # 绘制书名
    draw.text((x_offset, y_offset), "书名:", font=font_title, fill="black")
    y_offset += 40
    y_offset = draw_text_lines(draw, x_offset, y_offset, title_lines, font_text)

    # 绘制作者
    y_offset += 20
    draw.text((x_offset, y_offset), "作者:", font=font_title, fill="black")
    y_offset += 40
    y_offset = draw_text_lines(draw, x_offset, y_offset, author_lines, font_text)

    # 绘制年份
    y_offset += 20
    draw.text((x_offset, y_offset), "年份:", font=font_title, fill="black")
    y_offset += 40
    y_offset = draw_text_lines(draw, x_offset, y_offset, year_lines, font_text)

    # 绘制简介
    y_offset += 20
    draw.text((x_offset, y_offset), "简介:", font=font_title, fill="black")
    y_offset += 40
    y_offset = draw_text_lines(draw, x_offset, y_offset, description_lines, font_text)
    p=random_str() #你妈的，到底为什么
    save_path=f"data/pictures/cache/{p}.jpg"
    #sleep(2)
    canvas.save(save_path, "JPEG")
    return save_path




  # 纹理图片路径
#canvas = create_book_image(data, texture_path)
#canvas.show()
