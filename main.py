
from plugins.core.yamlLoader import YAMLManager


from plugins.utils.websocket_fix import ExtendBot
from run import api_implements, aiReply, user_data, resource_search, basic_plugin, aiDraw
from run.acg_infromation import galgame,bangumi
from run.groupManager import group_manager, self_Manager, wifeyouwant

config = YAMLManager(["config/settings.yaml",
                      "config/basic_config.yaml",
                      "config/api.yaml",
                      "config/controller.yaml",
                      "data/censor/censor_group.yaml",
                      "data/censor/censor_user.yaml"]) #这玩意用来动态加载和修改配置文件
#from developTools.adapters.http_adapter import HTTPBot
#bot = HTTPBot(http_sever=config.basic_config["adapter"]["http_client"]["url"],access_token=config.basic_config["adapter"]["access_token"],host=str(config.basic_config['adapter']["http_sever"]["host"]), port=int(config.basic_config["adapter"]["http_sever"]["port"]))
#或者使用ws适配器
bot = ExtendBot(config.basic_config["adapter"]["ws_client"]["ws_link"],config)


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


bot.run() #本地8080端口运行，onebot实现的http上报就填这个

