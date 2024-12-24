事件类型抄袭自[yiri-onebot](https://github.com/YiriMiraiProject/YiriOneBot)
部署此项目，你需要
1.启用onebot实现的http事件上报和http服务
```yaml
关于http服务，默认为3000，空access_token，可以自己设置
bot = HTTPBot(http_sever="http://127.0.0.1:3000",access_token="any_access_token")

然后是http事件上报，如果你设置了http上报地址为
http://localhost:8080/
那么，本项目主函数中，就是这样
bot.run(host="0.0.0.0", port= 8080)
```