import logging

import yaml
from yiriob.adapters import ReverseWebsocketAdapter
from yiriob.bot import Bot
from yiriob.event import EventBus

from plugins.tookits import newLogger
from plugins.yiriob_fix.YamlDotDict import ExtendedBot
from run import example, aiReply, FragmentsModule, aronaapi, aiDraw, musicPick

#读取配置
with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.load(f.read(), Loader=yaml.FullLoader)
bus = EventBus()
config_files = {
    'api': 'config/api.yaml',
    'settings': 'config/settings.yaml',
    "controller": "config/controller.yaml",
}

# 初始化扩展的机器人类
bot = ExtendedBot(
    adapter=ReverseWebsocketAdapter(
        host=str(config['ReverseWebsocketHost']), port=int(config['ReverseWebsocketPort']), access_token=str(config['access_token']), bus=bus
    ),
    self_id=int(config['bot_id']),
    config_files=config_files  # 传入多个 YAML 配置文件
)


logger=newLogger()

#与yiri mirai不同，我们需要传入bot和bus两个对象
#example.main(bot,bus,logger)  #这是一个测试示例，你可以参考它
#aiReply.main(bot,bus,logger)  #ai回复功能
musicPick.main(bot,bus,logger)  #调用musicPick插件
aronaapi.main(bot,bus,logger)  #调用aronaapi插件
FragmentsModule.main(bot,bus,logger)
aiDraw.main(bot,bus,logger)  #调用aiDrawer插件
bot.run()
