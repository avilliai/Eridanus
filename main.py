
from plugins.core.yamlLoader import YAMLManager
from run import api_implements, aiReply, user_data, resource_search, basic_plugin, group_manager

config = YAMLManager(["config/settings.yaml","config/basic_config.yaml","config/api.yaml","config/controller.yaml"]) #这玩意用来动态加载和修改配置文件
#from developTools.adapters.http_adapter import HTTPBot
#bot = HTTPBot(http_sever=config.basic_config["adapter"]["http_client"]["url"],access_token=config.basic_config["adapter"]["access_token"],host=str(config.basic_config['adapter']["http_sever"]["host"]), port=int(config.basic_config["adapter"]["http_sever"]["port"]))
#或者使用ws适配器
from developTools.adapters.websocket_adapter import WebSocketBot
bot = WebSocketBot(config.basic_config["adapter"]["ws_client"]["ws_link"])


basic_plugin.main(bot,config) #加载basic_plusine插件
resource_search.main(bot,config) #加载资源搜索插件
aiReply.main(bot,config) #加载ai回复插件
user_data.main(bot,config)
api_implements.main(bot,config)
group_manager.main(bot,config)

bot.run() #本地8080端口运行，onebot实现的http上报就填这个

