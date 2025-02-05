import asyncio
from developTools.event.events import GroupMessageEvent
from developTools.message.message_components import Image, Node, Text, File
from plugins.engine_search import baidu_search, searx_search

async def search_net(bot,event,config,query):
    functions = [
        baidu_search(query),
        searx_search(query)
    ]
    
    tasks = [asyncio.create_task(func) for func in functions]
    final = ''
    sendMes = []
    for future in asyncio.as_completed(tasks):
        try:
            result = await future
            if result:
                sendMes.append(Node(content=[Text(result)]))
                final += result + '\n'
        except Exception as e:
            bot.logger.error(f"{e}")
    await bot.send(event, sendMes)
    return  {"result": final}

def main(bot,config):
    @bot.on(GroupMessageEvent)
    async def search111(event):
        if str(event.raw_message).startswith("#搜索 "):
            query = str(event.raw_message).replace("#搜索 ", "")
            functions = [
                baidu_search(query),
                searx_search(query)
            ]
            
            tasks = [asyncio.create_task(func) for func in functions]
            sendMes = []
            for future in asyncio.as_completed(tasks):
                try:
                    result = await future
                    if result:
                        sendMes.append(Node(content=[Text(result)]))
                except Exception as e:
                    bot.logger.error(f"{e}")
            await bot.send(event, sendMes)
        else:
            pass