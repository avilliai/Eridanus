# coding=utf-8
import asyncio

from run.acg_infromation.service.majsoul.majsoul_info.majsoul_Spider import getID, gettriID
from run.acg_infromation.service.majsoul.majsoul_info.processData import printBasicInfo, printExtendInfo, \
    printRecordInfo


#@sv.on_prefix(('雀魂信息','雀魂查询'))
async def majsoulInfo(context):
    args = context.split()
    if len(args) == 1:
        nickname = context
        if len(nickname) > 15:
            return False,"昵称长度超过雀魂最大限制"
        message = ""
        IDdata = getID(nickname)
        if IDdata == -404:
            return False,   "获取牌谱屋的数据超时了呢，请稍后再试哦~"
        #sv.logger.info("正在查询" + nickname + "的对局数据")
        if IDdata == -1:
            return False,   "没有查询到该角色在金之间以上的对局数据呢~"
        else:
            if len(IDdata)>1:
                message = message + "查询到多条角色昵称呢~，若输出不是您想查找的昵称，请补全查询昵称\n\n"
                message = message + printBasicInfo(IDdata[0],"0","4")
            else:
                message = message+printBasicInfo(IDdata[0],"0","4")
            return True,message
    elif len(args) == 2:
        nickname = args[1]
        if len(nickname) > 15:
            return False,"昵称长度超过雀魂最大限制"
            #sv.logger.info("正在查询" + nickname + "的对局数据 ")
        message = ""
        room_level = ""
        if args[0] == "金场" or args[0] == "金" or args[0] == "金之间":
            room_level = "1"
        elif args[0] == "玉场" or args[0] == "玉" or args[0] == "玉之间":
            room_level = "2"
        elif args[0] == "王座" or args[0] == "王座之间":
            room_level = "3"
        else:
            return False,"房间等级输入不正确，请重新输入"
        IDdata = getID(nickname)
        if IDdata == -404:
            return False,   "获取牌谱屋的数据超时了呢，请稍后再试哦~"
        if IDdata == -1:
            return False,   "没有查询到该角色在金之间以上的对局数据呢~"
        else:
            if len(IDdata) > 1:
                message = message + "查询到多条角色昵称呢~，若输出不是您想查找的昵称，请补全查询昵称\n"
                message = message + printExtendInfo(IDdata[0], room_level,"4")
                return True,message
            else:
                pic = printExtendInfo(IDdata[0], room_level,"4")
                return True,pic
    else:
        return False,"查询信息输入不正确，请重新输入"


    #@sv.on_prefix(('雀魂牌谱','牌谱查询'))
async def RecordInfo(context):
    nickname = context
    if len(nickname) > 15:
        return False,  "昵称长度超过雀魂最大限制，已跳过"
    IDdata = getID(nickname)
    if IDdata == -404:
        return False,   "获取牌谱屋的数据超时了呢，请稍后再试哦~"
    message = ""
    #sv.logger.info("正在查询" + nickname + "的牌谱数据")
    if IDdata == -1:
        return False,   "没有查询到该角色在金之间以上的对局数据呢~"
    else:
        if len(IDdata) > 1:
            message = message + "查询到多条角色昵称呢~，若输出不是您想查找的昵称，请补全查询昵称\n"
            message = message + printRecordInfo(IDdata[0],4)
        else:
            message = message + printRecordInfo(IDdata[0],4)
        return True,message



    #@sv.on_prefix(('三麻信息','三麻查询'))
async def TrimajsoulInfo(context):
    args = context.split()
    if len(args) == 1:
        nickname = context
        if len(nickname) > 15:
            return False,  "昵称长度超过雀魂最大限制，已跳过"
        message = ""
        #sv.logger.info("正在查询" + nickname + "的对局数据")
        IDdata = gettriID(nickname)
        if IDdata == -404:
            return False,    "获取牌谱屋的数据超时了呢，请稍后再试哦~"
        if IDdata == -1:
            return False,   "没有查询到该角色在金之间以上的对局数据呢~"
        else:
            if len(IDdata)>1:
                message = message + "查询到多条角色昵称呢~，若输出不是您想查找的昵称，请补全查询昵称\n\n"
                message = message + printBasicInfo(IDdata[0],"0","3")
            else:
                message = message + printBasicInfo(IDdata[0],"0","3")
            return True,message
    elif len(args) == 2:
        nickname = args[1]
        if len(nickname) > 15:
            return False,  "昵称长度超过雀魂最大限制"
            #sv.logger.info("正在查询" + nickname + "的对局数据")
        message = ""
        room_level = ""
        if args[0] == "金场" or args[0] == "金" or args[0] == "金之间":
            room_level = "1"
        elif args[0] == "玉场" or args[0] == "玉" or args[0] == "玉之间":
            room_level = "2"
        elif args[0] == "王座" or args[0] == "王座之间":
            room_level = "3"
        else:
            return False,  "房间等级输入不正确，请重新输入"
            #sv.logger.info("正在查询" + nickname + "的对局数据")
        IDdata = gettriID(nickname)
        if IDdata == -404:
            return False,   "获取牌谱屋的数据超时了呢，请稍后再试哦~"
        if IDdata == -1:
            return False,   "没有查询到该角色在金之间以上的对局数据呢~"
        else:
            if len(IDdata) > 1:
                message = message + "查询到多条角色昵称呢~，若输出不是您想查找的昵称，请补全查询昵称\n"
                message = message + printExtendInfo(IDdata[0], room_level,"3")
                return True, message
            else:
                pic = printExtendInfo(IDdata[0], room_level,"3")
                return True, pic
    else:
        return False,  "查询信息输入不正确，请重新输入"

    #@sv.on_prefix('三麻牌谱')
async def TriRecordInfo(context):
    nickname = context
    if len(nickname) > 15:
        #sv.logger.info("昵称长度超过雀魂最大限制，已跳过")
        return False,  "昵称长度超过雀魂最大限制，已跳过"
    IDdata = gettriID(nickname)
    #sv.logger.info("正在查询" + nickname + "的牌谱数据")
    message = ""
    if IDdata == -1:
        #await bot.send(ev, "没有查询到该角色在金之间以上的对局数据呢~")
        return False,   "没有查询到该角色在金之间以上的对局数据呢~"
    else:
        if len(IDdata) > 1:
            message = message + "查询到多条角色昵称呢~，若输出不是您想查找的昵称，请补全查询昵称\n"
            message = message + printRecordInfo(IDdata[0],3)
            #await bot.send(ev, message, at_sender=True)
        else:
            message = message + printRecordInfo(IDdata[0],3)
            #await bot.send(ev, message, at_sender=True)
        return True,message

if __name__ == "__main__":
    asyncio.run(TriRecordInfo("CGhitomi"))