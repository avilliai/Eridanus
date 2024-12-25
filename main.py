
from developTools.AdapterAndBot import HTTPBot
from plugins.core.yamlLoader import YAMLManager
from run import example, aiReply, user_data
config = YAMLManager(["config/basic_config.yaml","config/api.yaml","config/controller.yaml"]) #这玩意用来动态加载和修改配置文件
#http_server地址，access_token
bot = HTTPBot(http_sever=config.basic_config["adapter"]["http_client"]["url"],access_token=config.basic_config["adapter"]["access_token"])

aiReply.main(bot,config) #加载ai回复插件
user_data.main(bot,config)
example.main(bot,config)

bot.run(host=str(config.basic_config['adapter']["http_sever"]["host"]), port=int(config.basic_config["adapter"]["http_sever"]["port"])) #本地8080端口运行，onebot实现的http上报就填这个

