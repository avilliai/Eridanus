import logging

import yaml
from yiriob.adapters import ReverseWebsocketAdapter
from yiriob.bot import Bot
from yiriob.event import EventBus


from plugins.tookits import newLogger
from run import example, aiReply

#读取配置
with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.load(f.read(), Loader=yaml.FullLoader)
bus = EventBus()
bot = Bot(
    adapter=ReverseWebsocketAdapter(
        host=str(config["ReverseWebsocketHost"]), port=config["ReverseWebsocketPort"], access_token=config["access_token"], bus=bus
    ),
    self_id=int(config["机器人QQ"]),
)

logger=newLogger()

#与yiri mirai不同，我们需要传入bot和bus两个对象
example.main(bot,bus,logger)  #这是一个测试示例，你可以参考它
aiReply.main(bot,bus,logger)  #ai回复功能

bot.run()
