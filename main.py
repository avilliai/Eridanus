import os
import sys
import asyncio
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from plugins.core.yamlLoader import YAMLManager
if sys.platform == 'win32':
  asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
from plugins.utils.websocket_fix import ExtendBot

config = YAMLManager(["config/settings.yaml",
                      "config/basic_config.yaml",
                      "config/api.yaml",
                      "config/controller.yaml",
                      "data/censor/censor_group.yaml",
                      "data/censor/censor_user.yaml",
                      "data/media_service/bilibili/bili_dynamic.yaml",
                      "data/tasks/scheduledTasks.yaml",
                      "data/tasks/scheduledTasks_push_groups.yaml",
                      "data/recognize/doro.yaml",
                      "data/recognize/nailong.yaml",]) #这玩意用来动态加载和修改配置文件
#from developTools.adapters.http_adapter import HTTPBot
#bot = HTTPBot(http_sever=config.basic_config["adapter"]["http_client"]["url"],access_token=config.basic_config["adapter"]["access_token"],host=str(config.basic_config['adapter']["http_sever"]["host"]), port=int(config.basic_config["adapter"]["http_sever"]["port"]))
#或者使用ws适配器
bot = ExtendBot(config.basic_config["adapter"]["ws_client"]["ws_link"],config,blocked_loggers=["DEBUG", "INFO_MSG"])
from run.anime_game_service import blue_archive
from run import api_implements, aiReply, user_data, basic_plugin, aiDraw
from run.resource_search import iwara, resource_search, engine_search
from run.acg_infromation import galgame,bangumi
from run.groupManager import group_manager, self_Manager, wifeyouwant, nailong_get
from run.streaming_media import youtube,bilibili,Link_parsing

aiDraw.main(bot,config) #加载aiDraw插件
basic_plugin.main(bot,config) #加载basic_plusine插件
resource_search.main(bot,config) #加载资源搜索插件
aiReply.main(bot,config) #加载ai回复插件
user_data.main(bot,config)
api_implements.main(bot,config)
self_Manager.main(bot,config)
group_manager.main(bot, config)
galgame.main(bot, config)#加载galgame回复插件
bangumi.main(bot, config) #加载bangumi插件

wifeyouwant.main(bot, config) #加载wifeyouwant插件
iwara.main(bot, config)
youtube.main(bot, config) #加载youtube插件
bilibili.main(bot, config) #加载bilibili插件
Link_parsing.main(bot, config)
engine_search.main(bot, config)

#以下为游戏相关
blue_archive.main(bot, config) #加载blue_archive插件
#奶龙检测
try:
    if config.settings["抽象检测"]["奶龙检测"] or config.settings["抽象检测"]["doro检测"]:
        nailong_get.main(bot, config)
except Exception as e:
    bot.logger.warning("【可选功能】奶龙检测相关依赖未安装，如有需要，请使用安装ai检测必要素材")

bot.run() #本地8080端口运行，onebot实现的http上报就填这个

