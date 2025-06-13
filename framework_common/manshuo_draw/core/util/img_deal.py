from PIL import Image, ImageDraw, ImageFont, ImageOps,ImageFilter
from .download_img import process_img_download
import math

def img_process(params,pure_backdrop ,img ,x_offset ,current_y ,upshift=0,type='img'):
    # 圆角处理
    if params['is_rounded_corners_front'] and params[f'is_rounded_corners_{type}']:
        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0, img.width, img.height), radius=params[f'rounded_{type}_radius'], fill=255, outline=255,
                               width=2)
        rounded_image = Image.new("RGBA", img.size)
        rounded_image.paste(img, (0, 0), mask=mask)
        img = rounded_image

    # 阴影处理
    if params['is_shadow_front'] and params[f'is_shadow_{type}']:
        shadow_image = Image.new("RGBA", pure_backdrop.size, (0, 0, 0, 0))  # 初始化透明图层
        shadow_draw = ImageDraw.Draw(shadow_image)
        # 计算阴影矩形的位置
        shadow_rect = [
            x_offset - params[f'shadow_offset_{type}'],  # 左
            current_y - params[f'shadow_offset_{type}'] + upshift,  # 上
            x_offset + img.width + params[f'shadow_offset_{type}'],  # 右
            current_y + img.height + params[f'shadow_offset_{type}'] + upshift  # 下
        ]
        # 绘制阴影（半透明黑色）
        shadow_draw.rounded_rectangle(shadow_rect, radius=params[f'rounded_{type}_radius'],
                                      fill=(0, 0, 0, params[f'shadow_opacity_{type}']))
        # 对阴影层应用模糊效果
        shadow_image = shadow_image.filter(ImageFilter.GaussianBlur(params[f'blur_radius_{type}']))
        # 将阴影层与底层图像 layer2 合并
        pure_backdrop = Image.alpha_composite(pure_backdrop, shadow_image)

    # 描边处理
    if params['is_stroke_front'] and params[f'is_stroke_{type}']:
        shadow_image = Image.new('RGBA', (img.width + params[f'stroke_{type}_width'], img.height + params[f'stroke_{type}_width']),
                                 (255, 255, 255, 80))
        shadow_blurred = shadow_image.filter(ImageFilter.GaussianBlur(params[f'stroke_{type}_width'] / 2))
        mask = Image.new('L', shadow_blurred.size, 255)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([0, 0, shadow_blurred.size[0], shadow_blurred.size[1]],
                               radius=params[f'stroke_{type}_radius'], fill=0, outline=255, width=2)
        shadow_blurred = ImageOps.fit(shadow_blurred, mask.size, method=0, bleed=0.0, centering=(0.5, 0.5))
        mask = ImageOps.invert(mask)
        shadow_blurred.putalpha(mask)
        pure_backdrop.paste(shadow_blurred,
        (int(x_offset - params[f'stroke_{type}_width'] / 2), int(current_y - params[f'stroke_{type}_width'] / 2 + upshift)),
                            shadow_blurred.split()[3])

    # 检查透明通道
    if img.mode == "RGBA":
        pure_backdrop.paste(img, (int(x_offset), int(current_y + upshift)), img.split()[3])
    else:
        pure_backdrop.paste(img, (int(x_offset), int(current_y + upshift)))

    return pure_backdrop


def backdrop_process(params,canves,limit=(0, 0)):
    limit_x, limit_y = limit
    if params['background'] is not None and params['background'] != 'None':
        params['background'] = process_img_download(params['background'], params['is_abs_path_convert'])
        if params['background'][0].width > limit_x and params['background'][0].height > limit_y:
            params['background'][0] = params['background'][0].resize((int(limit_x), int(limit_x * params['background'][0].height / params['background'][0].width)))
        if params['background'][0].height < limit_y:
            params['background'][0] = params['background'][0].resize((int((limit_y) * params['background'][0].width / params['background'][0].height), int(limit_y)))
        if params['background'][0].width < limit_x:
            params['background'][0] = params['background'][0].resize(
                (int(limit_x), int(limit_x * params['background'][0].height / params['background'][0].width)))
        params['background'][0] = params['background'][0].crop((0, 0, limit_x, limit_y))

        width, height = params['background'][0].size
        center_x, center_y = width // 2, height // 2
        shadow_color = (0, 0, 0)
        # 创建空白遮罩图像
        mask = Image.new("L", (width, height), 0)  # 单通道（L模式）
        draw = ImageDraw.Draw(mask)
        max_alpha,intensity = 100,1.5
        # 创建径向渐变（非线性）
        max_distance = math.sqrt(center_x ** 2 + center_y ** 2)  # 从中心到角落的最大距离
        for y in range(height):
            for x in range(width):
                # 计算像素点到中心的距离
                dx = x - center_x
                dy = y - center_y
                distance = math.sqrt(dx ** 2 + dy ** 2)

                # 根据距离计算透明度，使用非线性公式
                normalized_distance = distance / max_distance  # 距离归一化到 [0, 1]
                alpha = int(max_alpha * (normalized_distance ** intensity))  # 非线性加深
                if alpha > max_alpha:
                    alpha = max_alpha
                mask.putpixel((x, y), alpha)

        # 创建阴影图层
        shadow = Image.new("RGBA", params['background'][0].size, shadow_color + (0,))
        shadow.putalpha(mask)

        # 合并原图和阴影
        params['background'][0] = Image.alpha_composite(params['background'][0].convert("RGBA"), shadow)

        params['background'][0].paste(canves, (0, 0), mask=canves)
        canves = params['background'][0]
    return canves

def icon_process(params,canves,box_right=(0, 0)):
    x, y = box_right
    if params['right_icon'] is None or params['right_icon'] == 'None': return canves
    icon_img = process_img_download(params['right_icon'], params['is_abs_path_convert'])[0].convert("RGBA")
    icon_img = icon_img.resize((int(params['avatar_size'] * icon_img.width / icon_img.height), int(params['avatar_size'] )))
    if params['is_shadow_font']:
        color_image = Image.new("RGBA", icon_img.size, (255,255,255,255))
        color_image.putalpha(icon_img.convert('L'))
        canves.paste(color_image, (int(x - icon_img.width + 1), int(y - icon_img.height + 1)))

    canves.paste(icon_img, (int(x - icon_img.width), int(y - icon_img.height)), mask=icon_img)
    return canves