from PIL import Image, ImageSequence  # 添加 ImageSequence
from concurrent.futures import ThreadPoolExecutor
import os
import numpy as np
import asyncio
import tempfile  # 添加 tempfile 导入
import aiofiles  # 添加 aiofiles 导入
import io
# ...existing code...

# 移除 imageio 的导入
# import imageio.v2 as imageio #

# 修改 read_image_async 使用 asyncio.to_thread
async def read_image_async(image_path):
    """
    异步读取图片文件并返回 PIL Image 对象。
    """
    async with aiofiles.open(image_path, 'rb') as f:
        data = await f.read()
    img = await asyncio.to_thread(Image.open, io.BytesIO(data))
    return img.convert("RGBA")


async def get_gif_name(image):
    """
    根据输入的image名称，获取gif的生成路径和名称。
    """
    return os.path.join(
        os.path.dirname(image),
        os.path.splitext(os.path.basename(image))[0] + ".gif"
    )

# 修改 generate_blank_img 使用 asyncio.to_thread
async def generate_blank_img(img):
    """
    根据源图片生成同样大小的空白帧(默认为黑色)。
    使用内存中的 BytesIO 代替临时文件。
    """
    h, w, _ = img.shape
    blank_image = Image.new("RGBA", (w, h))
    img_byte_arr = io.BytesIO()
    await asyncio.to_thread(blank_image.save, img_byte_arr, format='PNG')
    data = img_byte_arr.getvalue()
    blank_img = await asyncio.to_thread(Image.open, io.BytesIO(data))
    return blank_img.convert("RGBA")


async def generate_gif_1(image, duration=[0.01, 9.99]):
    """
    使用添加空白帧的方法生成gif图像。
    """
    img = await read_image_async(image)  # 使用 read_image_async 获取已转换的图像
    bk_img = await generate_blank_img(np.array(img))
    img_list = [Image.fromarray(bk_img), img]
    gif_name = await get_gif_name(image)
    img_list[0].save(
        gif_name,
        save_all=True,
        append_images=img_list[1:],
        duration=[d * 1000 for d in duration],
        loop=0
    )

async def get_stripe_imgs(img, stripe_width=1):
    """
    获取得到两张条纹化的图像对象(此函数用于调试条纹宽度)。
    """
    h, w, _ = img.shape
    stripe_num = h // (stripe_width*2)
    img1 = img.copy()
    img2 = img.copy()
    
    for i in range(stripe_num):
        # 对第一张图片进行处理
        img1[i*2*stripe_width: (i*2+1)*stripe_width, :, :] = 255
        # 对第二章图片进行处理
        img2[(i*2+1)*stripe_width: (i*2+2)*stripe_width, :, :] = 255
    
    return [img1, img2]

def analyze_image_brightness(img_np):
    """
    分析图片整体明暗程度
    返回True表示偏白，False表示偏黑
    """
    # 计算RGB通道的平均值（忽略alpha通道）
    mean_value = np.mean(img_np[..., :3])
    # 如果平均值大于127.5（255的一半），则认为偏白
    #print(mean_value > 127.5)
    return mean_value <= 127.5

async def generate_stripe_imgs(image, stripe_height=1, stripe_gap=1, invert_color=False):
    """
    生成两个条纹化图像(png格式)，确保上一帧被条纹覆盖的部分在下一帧一定会显示
    """
    img_obj = await asyncio.to_thread(Image.open, image)
    img_obj = img_obj.convert("RGBA")
    img_np = np.array(img_obj)
    w, h = img_obj.size
    
    # 判断图片整体明暗
    is_bright = analyze_image_brightness(img_np)
    # 根据明暗选择条纹颜色
    stripe_color = 0 if is_bright else 255
    
    # 创建两个图像数组
    stripe_img1 = np.full_like(img_np, 255)  # 创建全白底图
    stripe_img2 = np.full_like(img_np, 255)  # 创建全白底图
    
    # 计算条纹间隔和数量
    stripe_interval = stripe_height + stripe_gap
    stripe_num = h // stripe_interval
    
    # 添加条纹效果（交替显示内容）
    for i in range(stripe_num):
        # 第一帧的内容和条纹
        content_pos1 = i * stripe_interval + stripe_height
        content_end1 = min((i + 1) * stripe_interval, h)
        if content_pos1 < h:
            # 添加图像内容
            stripe_img1[content_pos1:content_end1] = img_np[content_pos1:content_end1]
            # 添加条纹
            stripe_pos1 = i * stripe_interval
            stripe_end1 = min(stripe_pos1 + stripe_height, h)
            stripe_img1[stripe_pos1:stripe_end1, :, :3] = stripe_color
            stripe_img1[stripe_pos1:stripe_end1, :, 3] = 255

        # 第二帧的内容和条纹
        content_pos2 = i * stripe_interval
        content_end2 = min(i * stripe_interval + stripe_height, h)
        if content_pos2 < h:
            # 添加图像内容
            stripe_img2[content_pos2:content_end2] = img_np[content_pos2:content_end2]
            # 添加条纹
            stripe_pos2 = content_pos1
            stripe_end2 = content_end1
            if stripe_pos2 < h:
                stripe_img2[stripe_pos2:stripe_end2, :, :3] = stripe_color
                stripe_img2[stripe_pos2:stripe_end2, :, 3] = 255
    
    # 如果需要反转颜色，在添加条纹后进行反转
    if invert_color:
        stripe_img1 = await invert_colors(stripe_img1)
        stripe_img2 = await invert_colors(stripe_img2)
    
    return [stripe_img1, stripe_img2]

async def generate_gif_2(image):
    """
    使用拼接条纹化图片的形式生成gif图像。
    """
    gif_name = await get_gif_name(image)
    img_list = [Image.fromarray(arr) for arr in await generate_stripe_imgs(image)]
    img_list[0].save(
        gif_name,
        save_all=True,
        append_images=img_list[1:],
        duration=5,
        loop=0
    )

# 确保 invert_colors 也是异步的
async def invert_colors(image):
    """
    反转图像颜色(与安卓系统的颜色反转逻辑一致)
    """
    return await asyncio.to_thread(_invert_colors_sync, image)
def _invert_colors_sync(image):
    android_matrix = np.array([
        [-0.402, 1.174, 0.228],
        [ 0.598, 0.174, 0.228],
        [ 0.599, 1.175,-0.772]
    ], dtype=np.float32)
    normalized = image[..., :3].astype(np.float32) / 255.0
    transformed = np.dot(normalized, android_matrix.T)
    transformed = 1.0 - transformed
    transformed = np.clip(transformed, 0.0, 1.0)
    image[..., :3] = (transformed * 255.0).astype(np.uint8)
    return image

# 修改 process_single_image 确保所有步骤异步执行
async def process_single_image(image_path, blank_duration_s=0.5, stripe_duration=0.1, loop=0,
                               stripe_height=2, stripe_gap=1, use_blank_frame=True,
                               num_blank_frames=1, invert_color=False, output_folder="processed_gifs"):
    """
    处理单张图片，添加黑色首帧和交替闪烁的条纹效果
    """
    try:
        img = await read_image_async(image_path)
        img_np = np.array(img)
        h, w, channels = img_np.shape

        # 生成首帧
        if channels == 4:
            first_frame = await asyncio.to_thread(Image.new, "RGBA", (w, h), (0, 0, 0, 255) if not invert_color else (255, 255, 255, 255))
        else:
            first_frame = await asyncio.to_thread(Image.new, "RGB", (w, h), (0, 0, 0) if not invert_color else (255, 255, 255))

        # 生成条纹图像
        stripe_imgs = await generate_stripe_imgs(image_path, stripe_height, stripe_gap, invert_color)

        frames = []
        durations = []

        if use_blank_frame:
            for i in range(num_blank_frames):
                shade = int((i / max(num_blank_frames - 1, 1)) * 50)
                if channels == 4:
                    frame_np = np.array(first_frame)
                    frame_np[..., :3] = shade
                    frame = Image.fromarray(frame_np)
                else:
                    frame = await asyncio.to_thread(Image.new, "RGB", (w, h), (shade, shade, shade))
                frames.append(frame)
                durations.append(int(blank_duration_s * 1000))

        for _ in range(10):
            for stripe_img in stripe_imgs:
                frame = await asyncio.to_thread(Image.fromarray, stripe_img)
                frames.append(frame)
                durations.append(int(stripe_duration * 1000))

        # 异步保存GIF
        os.makedirs(output_folder, exist_ok=True)
        output_path = os.path.join(output_folder, os.path.splitext(os.path.basename(image_path))[0] + ".gif")
        await asyncio.to_thread(
            frames[0].save,
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=loop
        )
    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")
async def process_folder(input_folder, output_folder="processed_gifs", max_workers=4, blank_duration_s=0.016,
                        stripe_duration=0.016, loop=2, stripe_height=1, stripe_gap=1,
                        use_blank_frame=True, num_blank_frames=1, invert_color=False):
    """
    多线程处理文件夹中的所有图片 (异步方式)保存的图片名字相同，但是后缀为.gif
        # 直接设置处理参数
    INPUT_FOLDER = "adversarial_frames666"  # 输入文件夹路径
    OUTPUT_FOLDER = "processed_gifs"  # 输出文件夹路径
    params = {
        'blank_duration_s': 0.016,     # 空白首帧显示时间(单位s)
        'stripe_duration': 0.016,       # 条纹单帧显示时间(单位s)
        'num_blank_frames': 1,        # 空白首帧数量
        'loop': 2,                     # gif循环次数 (0表示无限循环)
        'stripe_height': 1,            # 条纹间隔高度(像素)(这个值通常和stripe_gap相同)
        'stripe_gap': 1,               # 每个条纹的固定高度(像素)(这个值通常和stripe_height相同)
        'max_workers': 4,              # 线程数（默认是4你可以提高这一项来增加处理速度，但是这可能会影响其他功能，所有不要太高）
        'use_blank_frame': True,       # 是否使用黑色首帧（这个参会控制blank_duration_s和num_blank_frames是否生效）
        'invert_color': False          # 新增参数：是否反转颜色，反转颜色后你可以在手机上开启反转颜色查看正常的颜色，这个绕过效果非常强，但是查看的时候必须要开启反转颜色
    }

    asyncio.run(process_folder(
        INPUT_FOLDER,
        output_folder=OUTPUT_FOLDER,
        max_workers=params['max_workers'],
        blank_duration_s=params['blank_duration_s'],
        stripe_duration=params['stripe_duration'],
        loop=params['loop'],
        stripe_height=params['stripe_height'],
        stripe_gap=params['stripe_gap'],  # 传递 stripe_gap 参数
        use_blank_frame=params['use_blank_frame'],
        num_blank_frames=params['num_blank_frames'],
        invert_color=params['invert_color']
    ))
    """
    os.makedirs(output_folder, exist_ok=True)
    image_files = [
        os.path.join(input_folder, f) for f in os.listdir(input_folder)
        if f.lower().endswith(('.png', '.jpg', '.jpeg'))
    ]
    semaphore = asyncio.Semaphore(max_workers)
    tasks = []

    async def sem_task(image_file):
        async with semaphore:
            await process_single_image(
                image_file,
                blank_duration_s=blank_duration_s,
                stripe_duration=stripe_duration,
                loop=loop,
                stripe_height=stripe_height,
                stripe_gap=stripe_gap,
                use_blank_frame=use_blank_frame,
                num_blank_frames=num_blank_frames,
                invert_color=invert_color,
                output_folder=output_folder
            )

    for image_file in image_files:
        tasks.append(asyncio.create_task(sem_task(image_file)))

    await asyncio.gather(*tasks)


async def compress_gifs(gif_paths, max_workers=4):
    """
    异步压缩GIF文件，直接覆盖源文件。

    参数:
        gif_paths (list): GIF文件的相对路径列表。
        max_workers (int): 使用的线程数，默认4。
    
    返回:
        list: 压缩后的GIF文件路径列表。
    """
    compressed_files = []
    queue = asyncio.Queue()

    # 将所有GIF路径加入队列
    for path in gif_paths:
        queue.put_nowait(path)

    def process_gif(gif_path,compress_colors=64,compress_pixels=589824):
        """
        处理并压缩单个GIF文件，直接覆盖源文件。

        参数:
            gif_path (str): GIF文件的相对路径。
            compress_colors (int): 压缩颜色数，默认64。提高此值可以增加图像质量，但会增加文件大小。
            compress_pixels (int): 压缩后的最大像素数，默认589824。超过此值的GIF文件将被缩小。
        
        返回:
            str or None: 压缩后的GIF文件路径，若出错则返回None。
        """
        try:
            with Image.open(gif_path) as img:
                frames = []
                for frame in ImageSequence.Iterator(img):
                    width, height = frame.size
                    pixels = width * height
                    if pixels > compress_pixels:
                        scale_factor = (compress_pixels / pixels) ** 0.5
                        new_size = (int(width * scale_factor), int(height * scale_factor))
                        frame = frame.resize(new_size, Image.LANCZOS)
                    frame = frame.convert('P', palette=Image.ADAPTIVE, colors=compress_colors)
                    frames.append(frame)
                
                # 覆盖保存压缩后的GIF
                frames[0].save(
                    gif_path,
                    save_all=True,
                    append_images=frames[1:],
                    optimize=True,
                    loop=img.info.get('loop', 0),
                    disposal=2  # 设置处置方法为背景
                )
            return gif_path
        except Exception as e:
            print(f"处理文件 {gif_path} 时出错: {e}")
            return None

    async def worker(executor):
        """
        工作协程，从队列中获取GIF路径并处理。

        参数:
            executor (ThreadPoolExecutor): 线程池执行器。
        """
        loop = asyncio.get_event_loop()
        while True:
            try:
                gif_path = await queue.get()
            except asyncio.CancelledError:
                break
            try:
                # 在线程池中运行处理函数
                result = await loop.run_in_executor(executor, process_gif, gif_path)
                if result:
                    compressed_files.append(result)
            except Exception as e:
                print(f"处理文件 {gif_path} 时发生异常: {e}")
            finally:
                queue.task_done()

    # 创建一个线程池执行器
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 启动多个工作协程
        tasks = [asyncio.create_task(worker(executor)) for _ in range(max_workers)]
        # 等待队列中的所有任务完成
        await queue.join()
        # 取消所有工作协程
        for task in tasks:
            task.cancel()
        # 等待所有工作协程真正取消
        await asyncio.gather(*tasks, return_exceptions=True)

    return compressed_files
""" if __name__ == "__main__":
    # 直接设置处理参数
    INPUT_FOLDER = "adversarial_frames666"  # 输入文件夹路径
    INPUT_FOLDER = "adversarial_frames666"  # 输入文件夹路径
    OUTPUT_FOLDER = "processed_gifs"  # 输出文件夹路径
    params = {
        'blank_duration_s': 0.016,     # 空白首帧显示时间(单位s)
        'stripe_duration': 0.016,       # 条纹单帧显示时间(单位s)
        'num_blank_frames': 3,        # 空白首帧数量
        'loop': 2,                     # gif循环次数 (0表示无限循环)
        'stripe_height': 1,            # 条纹间隔高度(像素)(这个值通常和stripe_gap相同)
        'stripe_gap': 1,               # 每个条纹的固定高度(像素)(这个值通常和stripe_height相同)
        'max_workers': 4,              # 线程数（默认是4你可以提高这一项来增加处理速度，但是这可能会影响其他功能，所有不要太高）
        'use_blank_frame': True,       # 是否使用黑色首帧（这个参会控制blank_duration_s和num_blank_frames是否生效）
        'invert_color': False          # 新增参数：是否反转颜色，反转颜色后你可以在手机上开启反转颜色查看正常的颜色，这个绕过效果非常强，但是查看的时候必须要开启反转颜色
    }

    asyncio.run(process_folder(
        INPUT_FOLDER,
        output_folder=OUTPUT_FOLDER,
        max_workers=params['max_workers'],
        blank_duration_s=params['blank_duration_s'],
        stripe_duration=params['stripe_duration'],
        loop=params['loop'],
        stripe_height=params['stripe_height'],
        stripe_gap=params['stripe_gap'],  # 传递 stripe_gap 参数
        use_blank_frame=params['use_blank_frame'],
        num_blank_frames=params['num_blank_frames'],
        invert_color=params['invert_color']
    ))
    print("All images processed.") """