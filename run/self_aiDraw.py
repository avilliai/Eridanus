from developTools.event.events import GroupMessageEvent
from developTools.message.message_components import Image, Text, Node
import asyncio
from plugins.draw_setting.drawing import get_prompt,draw,get_model_list
prompt,input_path,output_path = get_prompt()
draw_waiting_queue = asyncio.Queue()
draw_group_id = asyncio.Queue()
def main(bot,config):
    @bot.on(GroupMessageEvent)
    async def self_aiDraw(event: GroupMessageEvent):
        if event.message_chain.has(Text) and event.message_chain.get(Text)[0].text.startswith("draw") or event.message_chain.has(Text) and event.message_chain.get(Text)[0].text.startswith("重画"):
            info = event.message_chain
            global draw_waiting_queue
            await draw_waiting_queue.put(info)
            await bot.send(event,'当前画图等待队列长度：{} 请耐心等待~~'.format(draw_waiting_queue.qsize()-1))
            await draw_group_id.put(event.group_id)
            lst = await draw(bot,config,draw_waiting_queue,draw_group_id,prompt)
            await bot.send(event,Node(content=lst))
        elif event.message_chain.has(Text) and event.message_chain.get(Text)[0].text.startswith("模型列表"):
            bot.logger.info("模型列表!")
            lst = await get_model_list(prompt)
            info = lst[0]
            await bot.send(event,info)
        elif event.message_chain.has(Text) and event.message_chain.get(Text)[0].text.startswith("模型切换"):
            bot.logger.info("模型切换!")
            lst = await get_model_list(prompt)
            base_model = lst[1]
            # 按key切换
            model_name = event.message_chain.get(Text)[0].text.split(' ')[1]
            if model_name in base_model.keys():
                prompt["4"]["inputs"]["ckpt_name"] = base_model[model_name]
                await bot.send(event,Text('模型切换成功'))
            else:
                await bot.send(event,Text('模型不存在'))
