
from EridanusTools.AdapterAndBot import HTTPBot
from run import example

#http_server地址，access_token
bot = HTTPBot(http_sever="http://127.0.0.1:3000",access_token="any_access_token")

example.main(bot)

bot.run(host="0.0.0.0", port= 8080) #本地8080端口运行，onebot实现的http上报就填这个

