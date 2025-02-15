from developTools.event.events import GroupMessageEvent
from developTools.message.message_components import Image 
from plugins.petpet.petpet import pictureCompositing,gifSynthesis
import os
import shutil

async def frameProcessing(path, event, bot):
    try:
        # 获取背景图像路径
        bgImagePath = f"data/petpet/{path}/bgImage"

        # 获取背景文件夹下所有图像文件名，并按顺序排序
        img_files = sorted(
            [os.path.join(bgImagePath, f) for f in os.listdir(bgImagePath) if f.endswith(('.png', '.jpg'))],
            key=lambda x: int(os.path.splitext(os.path.basename(x))[0])
        )
        # 初始化文件夹路径
        save_path = None
        isLast=False #是否是最后一帧 

        # 循环处理每一帧
        for index, item in enumerate(img_files):
            if index+1==len(img_files):
                isLast=True
            save_path = pictureCompositing(item, index, path, event, isLast,save_path)
        gifName = gifSynthesis(save_path)  # 合成 GIF
        await bot.send(event, [Image(file=gifName)])
    finally:
        shutil.rmtree(save_path)
        os.remove(gifName)

def main(bot,config):
    @bot.on(GroupMessageEvent)
    async def cao(event):
        if event.raw_message.startswith("草") or event.raw_message.startswith("操") or event.raw_message.startswith("草死你") or event.raw_message.startswith("曹思妮"):
            # 每一帧图片合成位置
            await frameProcessing("cao",event,bot)
    
    @bot.on(GroupMessageEvent)
    async def purpleMood(event):
        if event.raw_message.startswith("紫色心情") or event.raw_message.startswith("想要紫色心情了是吧"):
            await frameProcessing("purple-mood",event,bot)


