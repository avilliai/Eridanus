from EridanusTools.event.events import GroupMessageEvent
from plugins.core.aiReplyCore import aiReplyCore
from plugins.core.llmDB import delete_user_history


async def prompt_elements_construct(precessed_message):
    prompt_elements=[]
    #{"role": "assistant","content":[{"type":"text","text":i["text"]}]}
    for i in precessed_message:
        if "text" in i:
            prompt_elements.append({"type":"text","text":i["text"]})
        elif "image" in i:
            prompt_elements.append({"type":"image_url","image_url":i["image"]["url"]})
        elif "record" in i:
            pass
            #prompt_elements.append({"type":"voice","voice":i["voice"]})
    return {"role": "user","content":prompt_elements}
def main(bot,config):
    @bot.on(GroupMessageEvent)
    async def aiReply(event):

        print(event.processed_message)

        if event.get("at") and event.get("at")[0]["qq"]==str(bot.id):
            #print(f"接受艾特消息{event.processed_message}")
            #bot.logger.info(f"{event.get('at')[0]}")
            bot.logger.info(f"接受艾特消息{event.processed_message}")
            ask=await prompt_elements_construct(event.processed_message)
            print(ask)
            r=await aiReplyCore(ask,event.user_id,config)
            await bot.send(event,r["content"])
        if event.raw_message=="/clear":
            await delete_user_history(event.user_id)
            await bot.send(event,"历史记录已清除")