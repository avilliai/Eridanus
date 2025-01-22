# -*- coding: utf-8 -*-
from developTools.event.events import GroupMessageEvent

async def operate_group_push_tasks(bot,event:GroupMessageEvent,config,task_type:str,operation:bool):
    if task_type=="asmr":
        if operation:
            if event.group_id in config.scheduledTasks_push_groups["latest_asmr_push"]["groups"]:
                await bot.send(event,"本群已经订阅过了")
                return
            else:
                config.scheduledTasks_push_groups["latest_asmr_push"]["groups"]=config.scheduledTasks_push_groups["latest_asmr_push"]["groups"].append(event.group_id)
                config.save("scheduledTasks_push_groups")
                await bot.send(event,"订阅成功")
        else:
            if event.group_id in config.scheduledTasks_push_groups.yaml["latest_asmr_push"]["groups"]:
                config.scheduledTasks_push_groups["latest_asmr_push"]["groups"]=config.scheduledTasks_push_groups["latest_asmr_push"]["groups"].remove(event.group_id)
                config.save("scheduledTasks_push_groups")
                await bot.send(event,"取消订阅成功")
            else:
                await bot.send(event,"本群没有订阅过")

def main(bot,config):

    @bot.on(GroupMessageEvent)
    async def _(event):
        pass
