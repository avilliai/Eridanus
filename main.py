
from developTools.AdapterAndBot import HTTPBot
from plugins.core.yamlLoader import YAMLManager
from run import example, aiReply

#http_server地址，access_token
bot = HTTPBot(http_sever="http://127.0.0.1:3000",access_token="any_access_token")
config = YAMLManager(["config/api.yaml","config/controller.yaml"]) #这玩意用来动态加载和修改配置文件

aiReply.main(bot,config) #加载ai回复插件
example.main(bot,config)

bot.run(host="0.0.0.0", port= 8080) #本地8080端口运行，onebot实现的http上报就填这个

