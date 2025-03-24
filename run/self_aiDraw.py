from developTools.event.events import GroupMessageEvent
from developTools.message.message_components import Image, Text, Node, Json
from plugins.random_pic.random_anime import get_text_number
import asyncio
import random
from time import sleep
import time
from plugins.draw_setting.drawing import get_images, download_image,get_prompt
import os
base_model = {"has":'hassakuXLIllustrious_v21.safetensors',"jru":'jruTheJourneyRemains_v27.safetensors',"obs":'obsessionIllustrious_vPredV11.safetensors',
              "waiN":'waiNSFWIllustrious_v120.safetensors',"waiS":'waiSHUFFLENOOB_vPred20.safetensors',"mis":'mistoonAnimeNoobai.CS46.safetensors',
              "alc":'alchemix20illustrious.lAYX.safetensors',"any":'AnythingXL_xl.safetensors',"cou":'counterfeitV30_v30.safetensors'}
random_model = random.choice(list(base_model.values()))
model_list = ", ".join(f"{k}: {v}" for k, v in base_model.items())
prompt,input_path,output_path = get_prompt()
def main(bot,config):
    @bot.on(GroupMessageEvent)
    async def self_aiDraw(event: GroupMessageEvent):
        if event.message_chain.has(Text) and event.message_chain.get(Text)[0].text.startswith("draw") or event.message_chain.has(Text) and event.message_chain.get(Text)[0].text.startswith("重画"):
            numbers = await get_text_number(bot,config,event)
            if 'random' in event.message_chain.get(Text)[0].text:
              prompt["4"]["inputs"]["ckpt_name"] = random_model
            #绘画模式
            if event.message_chain.get(Text)[0].text.startswith('draw'):
              text = event.message_chain.get(Text)[0].text.split('-')[2]
              #随机数防止fixed seed
              prompt["6"]["inputs"]["text"] =  text
            #重画模式
            if event.message_chain.get(Text)[0].text.startswith('重画'):
              image_url = event.message_chain.get(Image)[0].url
              image_name = image_url.split('/')[-1][-25:]+'.png'
              image_path = os.path.join(input_path, image_name)
              width, height = await download_image(image_url, image_path)
              #height, width = cv2.imread(image_path+'.png').shape[:2]
              if 1028< height < 1600:
                prompt["5"]["inputs"]["height"] = height
              if 760< width < 1152:
                prompt["5"]["inputs"]["width"] = width
              prompt["16"]["inputs"]["image"] = image_name
            bot.logger.info("画图!")            
            #prompt["4"]["inputs"]["ckpt_name"] = random_model
            prompt["5"]["inputs"]["batch_size"] = numbers
            await bot.send(event,'wait time less than {}s'.format(12*numbers))
            start_time = time.time()
            #delete_files(output_path)
            get_images(prompt)
            file_list = os.listdir(output_path)
            ori_file_len = len(file_list)
            while len(file_list) < ori_file_len + numbers:
                await asyncio.sleep(0.85)
                file_list = os.listdir(output_path)
            sleep(0.05)
            lst = []
            for file in file_list[-1:-numbers-1:-1]:
                if file.endswith('.png'):
                  img_path = os.path.join(output_path, file)
                  lst.append(Image(file=img_path))
            bot.logger.info('start sending')
            await bot.send(event,Node(content=lst))
            end_time = time.time()
            await bot.send(event,'practical time cost: {}s'.format(end_time - start_time))
        elif event.message_chain.has(Text) and event.message_chain.get(Text)[0].text.startswith("模型列表"):
            bot.logger.info("模型列表!")
            info = '模型列表：\n'+model_list+'当前模型：'+prompt["4"]["inputs"]["ckpt_name"]+'\n切换模型请按模式：模型切换 模型名(key)'
            await bot.send(event,info)
        elif event.message_chain.has(Text) and event.message_chain.get(Text)[0].text.startswith("模型切换"):
            bot.logger.info("模型切换!")
            # 按key切换
            model_name = event.message_chain.get(Text)[0].text.split(' ')[1]
            if model_name in base_model.keys():
                prompt["4"]["inputs"]["ckpt_name"] = base_model[model_name]
                await bot.send(event,Text('模型切换成功'))
            else:
                await bot.send(event,Text('模型不存在'))