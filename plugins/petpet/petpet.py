import os
import time
import tempfile
import urllib.request
from PIL import Image,ImageDraw
import cv2
import numpy as np
import uuid

# 下载网络图片到临时文件夹
def download_image(qq):
    save_path=f"data/petpet/temp_dir/{qq}.png"
    url=f"https://api.dwo.cc/api/qq?qq={qq}"
    try:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)  
        
        # 列出目录中的所有文件 如果当前有这个图片无需重复下载
        files = os.listdir("data/petpet/temp_dir")
        for filename in files:
            if filename[:-4] == qq:
                # 如果找到，抛出文件
                image = Image.open(save_path)
                return image


        #  没有这个图片 下载
        with open(save_path, 'wb') as f:
            with urllib.request.urlopen(url) as response:
                f.write(response.read())
        image = Image.open(save_path)
        return image
    except Exception as e:
        if os.path.exists(save_path):
            os.remove(save_path)
        raise e


def create_sequential_folder(base_path):
    counter = 1
    while True:
        new_path = f"{base_path}{counter}" if counter > 1 else base_path
        if not os.path.exists(new_path):
            os.makedirs(new_path, exist_ok=True)
            return new_path
        counter += 1



# 合成每一帧的图片
# bgImageSrc :背景图保存位置
# index ：背景图下标，用于命名帧的名字
# path ：调用的哪个petpet 用于建立唯一路径
def pictureCompositing(bgImageSrc, img_name, path, event, isLast,save_path=None):
    try:
        user_id = event.user_id
        
        # 检查是否有被at的人
        index = event.raw_message.find("qq=")
        if index != -1:
            at_qq = event.raw_message[index + 3:] 
            if ']' in at_qq:
                at_qq = at_qq.split(']')[0]
        else:
            at_qq = user_id
            user_id = event.self_id
        
        syImage1 = download_image(at_qq)  # 被动
        syImage2 = download_image(user_id)  # 主动

        background = Image.open(f"{bgImageSrc}").convert("RGBA")
        background_np = np.array(background)
        alpha = background_np[:, :, 3]
        transparent_mask = (alpha == 0).astype(np.uint8) * 255
        contours, _ = cv2.findContours(transparent_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 处理每个区域
        for i, contour in enumerate(contours):
            mask = np.zeros_like(alpha)
            cv2.drawContours(mask, [contour], -1, 255, -1)
            x, y, w, h = cv2.boundingRect(contour)
            
            # 处理填充图片
            if i == 0:
                fill_img = syImage1.convert("RGBA")
            else:
                fill_img = syImage2.convert("RGBA")

            fill_img = fill_img.resize((w, h))
            fill_np = np.array(fill_img)
            roi_mask = mask[y:y+h, x:x+w]
            fill_np[:, :, 3] = cv2.bitwise_and(fill_np[:, :, 3], roi_mask)
            fill_pil = Image.fromarray(fill_np)
            background.paste(fill_pil, (x, y), fill_pil)
            

        # 如果没有提供 save_path，表示是新任务，创建新的文件夹
        if save_path is None:
            save_path = create_sequential_folder(f"data/petpet/{path}-synthesis-frame")
    
        # 保存合成后的图像
        save_file_path = f"{save_path}/{img_name}.png"
        background.save(save_file_path)
        return save_path
    finally:
        if isLast:
            print("最后一帧 删除下载的qq头像")
            os.remove(f"data/petpet/temp_dir/{at_qq}.png")
            os.remove(f"data/petpet/temp_dir/{user_id}.png")


# 多张图片合成GIF
def gifSynthesis(img_folder):
    gif_filename = f'data/petpet/result/{uuid.uuid4()}.gif' #使用uuid作为唯一文件名
    # 获取所有图像文件名，并按顺序排序
    img_files = sorted(
    [os.path.join(img_folder, f) for f in os.listdir(img_folder) if f.endswith(('.png', '.jpg'))],
    key=lambda x: int(os.path.splitext(os.path.basename(x))[0]))

    img = Image.open(img_files[0])
    gif_frames = [img]
    for filename in img_files[1:]:
        img = Image.open(filename)
        gif_frames.append(img)
    # 保存GIF动画，并指定帧间隔时间和循环次数等参数
    gif_frames[0].save(
        gif_filename,
        save_all=True,
        append_images=gif_frames[1:],
        duration=100,  # 帧之间的延迟时间（以毫秒为单位）
        loop=0  # 循环次数（0表示无限循环）
    )
    return gif_filename

