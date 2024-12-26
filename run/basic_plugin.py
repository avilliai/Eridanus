from developTools.event.events import GroupMessageEvent
from developTools.message.message_components import Record, Node, Text
from plugins.basic_plugin.weather_query import weather_query
from plugins.core.aiReplyCore import aiReplyCore

"""
供func call调用
"""
async def call_weather_query(bot,event,config,location):
    r=await weather_query(config.api["proxy"]["http_proxy"],config.api["心知天气"]["api_key"],location)
    r = await aiReplyCore([{"text":f"请你为我播报接下来几天的天气{r}"}], event.user_id, config)
    await bot.send(event, str(r))
def main(bot,config):
    global avatar
    avatar=False
    @bot.on(GroupMessageEvent)
    async def sendLike(event: GroupMessageEvent):
        if event.raw_message.startswith("查天气"):
            #await bot.send(event, "已修改")
            remark = event.raw_message.split("查天气")[1].strip()
            await bot.set_friend_remark(event.user_id, remark)
