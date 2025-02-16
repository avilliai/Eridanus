from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import re

def add_rounded_rectangle(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
    draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)
    draw.pieslice([x0, y0, x0 + 2 * radius, y0 + 2 * radius], 180, 270, fill=fill)
    draw.pieslice([x1 - 2 * radius, y0, x1, y0 + 2 * radius], 270, 360, fill=fill)
    draw.pieslice([x0, y1 - 2 * radius, x0 + 2 * radius, y1], 90, 180, fill=fill)
    draw.pieslice([x1 - 2 * radius, y1 - 2 * radius, x1, y1], 0, 90, fill=fill)

def draw_netease_music_card(data, filepath, song_id):
    """
    绘制网易云音乐卡片预览图。
    :param data: 包含绘图所需数据的字典
    :param filepath: 文件保存路径
    :param song_id: 歌曲 ID
    """
    #加载封面图片
    cover_img = Image.open(data["cover_path"])
    #创建背景
    bg_size = (1024, 960)
    bg_img = cover_img.resize(bg_size).filter(ImageFilter.GaussianBlur(radius=50))
    draw = ImageDraw.Draw(bg_img)

    #设置字体
    font_size = 60
    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "fonts", "LXGWWenKai-Regular.ttf"))
    print(f"字体文件路径: {font_path}")
    try:
        font = ImageFont.truetype(font_path, font_size)
        font_small = ImageFont.truetype(font_path, 40)
        font_creator = ImageFont.truetype(font_path, 30)
    except Exception as e:
        print(f"加载字体失败: {e}")
        return

    #绘制文本
    text_color = (255, 255, 255)
    gray_color = (169, 169, 169)

    #放置封面图
    cover_size = (300, 300)
    cover_img = cover_img.resize(cover_size)
    mask = Image.new("L", cover_size, 0)
    mask_draw = ImageDraw.Draw(mask)
    add_rounded_rectangle(mask_draw, (0, 0, cover_size[0], cover_size[1]), radius=30, fill=255)
    cover_img_x = (bg_size[0] - cover_size[0]) // 2
    cover_img_y = 60
    bg_img.paste(cover_img, (cover_img_x, cover_img_y), mask)

    #歌曲类型
    song_type_text = data.get("song_type", "")
    song_type_y = cover_img_y + cover_size[1] + 20
    if song_type_text:
        bbox = draw.textbbox((0, 0), song_type_text, font=font_small)
        song_type_width = bbox[2] - bbox[0]
        song_type_x = (bg_size[0] - song_type_width) // 2
        draw.text((song_type_x, song_type_y), song_type_text, font=font_small, fill=gray_color)

    #歌曲名称
    song_name_y = song_type_y + 40 + 20
    song_name_lines, song_name_height = wrap_text(data["song_name"], font, 800)
    for line in song_name_lines[:2]:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        text_x = (bg_size[0] - line_width) // 2
        draw.text((text_x, song_name_y), line, font=font, fill=text_color)
        song_name_y += font_size + 10

    #歌手名称
    artist_name_lines, artist_name_height = wrap_text(data["artist_name"], font_small, 800)
    artist_name_y = song_name_y + 20
    for line in artist_name_lines[:1]:
        bbox = draw.textbbox((0, 0), line, font=font_small)
        line_width = bbox[2] - bbox[0]
        text_x = (bg_size[0] - line_width) // 2
        draw.text((text_x, artist_name_y), line, font=font_small, fill=text_color)
        artist_name_y += 40 + 10


    creator_text = "Created By QcrTiMo"
    bbox = draw.textbbox((0, 0), creator_text, font=font_creator)
    creator_text_width = bbox[2] - bbox[0]
    creator_text_x = (bg_size[0] - creator_text_width) // 2
    draw.text((creator_text_x, 880), creator_text, font=font_creator, fill=text_color)

    #保存图片
    output_path = f"{filepath}{song_id}.png"
    bg_img.save(output_path)
    return output_path

def wrap_text(text, font, max_width):
    lines = []
    current_line = []
    words = re.findall(r'\b\w+\b|[\s\.,;:\-\(\)\[\]\{\}!@#$%^&*+=_<>/?"`~]+', text)
    for word in words:
        bbox = font.getbbox("".join(current_line) + word)
        line_width = bbox[2] - bbox[0]
        if line_width > max_width:
            lines.append("".join(current_line))
            current_line = [word]
        else:
            current_line.append(word)
    if current_line:
        lines.append("".join(current_line))
    return lines, sum(font.getbbox(line)[3] - font.getbbox(line)[1] for line in lines)