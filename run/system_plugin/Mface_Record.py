from developTools.event.events import GroupMessageEvent
from developTools.message.message_components import Mface, Image, At

from framework_common.utils.utils import download_img

async def call_send_mface(bot,event,config,summary):
    await bot.send(event,Image(file=f"data/pictures/Mface/{summary}"))

def main(bot,config):

    @bot.on(GroupMessageEvent)
    async def record_mface(event: GroupMessageEvent):
        # 检查配置中是否允许收集表情包
        if not config.common_config.basic_config.get("record_mface", False):
            return
            
        if event.user_id==config.common_config.basic_config["master"]["id"]:
            if event.message_chain.has(Image) and event.message_chain.get(Image)[0].summary!="":
                summary = event.message_chain.get(Image)[0].summary
                url = event.message_chain.get(Image)[0].url
            elif event.message_chain.has(Mface):
                #print(event.message_chain.get(Mface)[0])
                mface=event.message_chain.get(Mface)[0]
                summary=mface.summary
                url=mface.url
            else:
                return
                #await bot.send(event,f"收到表情包：{summary}，地址：{url}")
            bot.logger.info(f"收到表情包：{summary}，地址：{url}")
            try:
                await download_img(url,f"data/pictures/Mface/{summary}.{url.split('.')[-1]}")
            except:
                bot.logger.error(f"下载表情包失败：{summary}，地址：{url}")
                
    @bot.on(GroupMessageEvent)
    async def send_mface(event: GroupMessageEvent):
        if event.message_chain.has(At) and event.message_chain.get(At)[0].qq==bot.id:
            pass
            """
            弄成概率插嘴
            """
