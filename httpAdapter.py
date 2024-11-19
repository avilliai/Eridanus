from typing import Dict

import uvicorn
from fastapi import FastAPI, Request

from EridanusCradle.bot import Bot
from EridanusCradle.events import GroupMessage, FriendMessage

app = FastAPI()

bot=Bot()
@app.post("/")
async def root(request: Request):
    data = await request.json()  # 获取事件数据
    print(data)
    r=await bot.handle_event(data)  # 让 Bot 类处理事件
    return r

@bot.on(GroupMessage)
async def handle_group(event: GroupMessage):
    print("处理群组消息事件:", event.raw_message)
    #await bot.send(f"您发送的群组消息是: {event.raw_message}", event.user_id)
@bot.on(FriendMessage)
async def handle_friend(event: FriendMessage):
    print("处理好友消息事件:", event.raw_message)
if __name__ == "__main__":
    uvicorn.run(app, port=8080)