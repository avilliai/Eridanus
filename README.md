>当前任务应集中在sdk的调整和修改，尽可能降低迁移过来的成本。同时兼顾继续开发的易用性。

基于[yiri-onebot](https://github.com/YiriMiraiProject/YiriOneBot)

对项目Manyana进行重新规划，不再使用overflow而是直接对接onebot实现，提高效率。

目前任务较为繁重，规划是，
- [ ] 1.更明确的plugins和run对应关系
- [ ] 2.run文件夹下各功能到yiriob的适配(目前进度<50%)
- [x] 3.优化配置文件结构
- [x] 4.功能触发方式改写(详见run/FragmentsModule.py，可作为仿写示例) 以及自定义触发规则
- [x] 5.优化data文件分布
- [ ] 6.更完善的一键更新工具
- [ ] 7.引入数据库进行用户数据统计和分析
- [ ] 8.语义分析功能触发，作为aiReplyCore的进一步升级，可能需要进一步修改功能触发方式，或通过继承yiriob的某些类，事先对接受的数据进行语义分析，然后再推送给具体的handler

# 开发注意事项
#### 1.注意,onebot实现必须开启 reverse websocket以及配置对应的access token，默认的空值疑似将导致yirionebot出错。

#### 2.yiriob目前无法在py39使用，请使用py3.11。

#### 3.yiriob的默认Logger级别是DEBUG，会出现大量日志输出影响调试。你可以修改`.venv/Lib/site-packages/yiriob/utils/logger.py`
```python
logging.basicConfig(
    level=logging.INFO,           #这里，修改为logging.INFO即可。
    handlers=[RichHandler()] if RichHandler is not None else [],
)

logger = logging.getLogger("yiri-bot")

__all__ = ["logger", "pprint"]
```

#### 4.在yirimirai编写代码的大部分思路在这里都是可以使用的。目前的任务集中在原Manyana/run文件夹下文件的重写<br>
yirimirai和yirionebot十分相似，以下面的代码为例，在很多地方你都可以使用你的开发工具直接替换对应的文本。
```python
@bus.on(GroupMessageEvent)
async def test(event:GroupMessageEvent):
    if event.raw_message=="你好":            #event.raw_message会包含CQ码，请搜索查阅相关文档，项目暂时用toolkits中的函数对文本内容进行判断，后续针对CQ码特点进行调整。。
        print(event.sender.user_id)
        await bot.send_group_message(event.group_id, [Reply(str(event.message_id)), Text("hello word")]) #Reply(str(event.message_id))即为引用
```
等价于
```python
@bot.on(GroupMessage)
async def test(event:GroupMessage):
    if str(event.message_chain)=="你好":
        print(event.sender.id)
        await bot.send_group_message(event.group.id, "hello word",True)
```
#### 5.若干常用类
```python
#几个参数分别是，艾特，文本，引用回复
await bot.send_group_message(event.group_id,[At(str(event.sender.user_id)),Text("你好"),Reply(str(event.message_id))])
#发送图片(目前file参数似乎只能用url)
await bot.send_group_message(event.group_id,[Image(file="imgurl",type='flash',url="")])
#发送语音(目前file参数似乎只能用url)
await bot.send_group_message(event.group_id,[Record(file="imgurl",url="")])
#MessageChain可以是一个列表，因此你可以构建出图文组合同时引用对方的回复
await bot.send_group_message(event.group_id,[Text("你好"),Reply(str(event.message_id)),Record(file="imgurl",url="")])
```
既然file参数只能用url,那如果我确实需要发送本地文件怎么办？这时候就要用到`file://`协议了，该协议用来访问本设备文件，我们可以以这种方式给Image类和Record类传参
```python
from pathlib import Path
#中间的部分省略
image_path = Path(f"{os.getcwd()}/plugins/NB2uR.png") #这一步，我们拼接出了img的绝对路径
file_url = image_path.as_uri()                        #利用Path的as_uri()即可取到 file://协议下的文件链接
await bot.send_group_message(event.group_id,[Image(file=file_url,type='flash',url="")])  #正常传参即可

#语音也是同理
#发送本地语音
image_path = Path(f"{os.getcwd()}/plugins/output.wav")
file_url = image_path.as_uri()
await bot.send_group_message(event.group_id, [Record(file=file_url,url="")])

#你也可以调用我们在toolkits.py中提供的函数，这样一行即可完成语音发送，图片也是同理

await bot.send_group_message(event.group_id, [Record(file=fileUrl("plugins/output.wav"),url="")])
```
完整的示例请查看run/example.py
#### 6.一些小寄巧
你可以直接替换一些内容，减少工作量
```
str(event.message_chain)
换成
wash_cqCode(event.raw_message)

At(bot.qq) in event.message_chain
换成
check_cq_atcode(event.raw_message,bot.id)  (返回的是一个bool，是否包含@bot)

@bot.on(GroupMessage)
换成
@bus.on(GroupMessageEvent)

原先的
async def func(event: GroupMessage):
中的GroupMessage也需要全部换成GroupMessageEvent

私聊同理，换成对应的事件。用查找并替换应该能减少不少工作量，还有一些其他的内容也可以这样做，比如event.sender.id换event.sender.user_id等。
```
