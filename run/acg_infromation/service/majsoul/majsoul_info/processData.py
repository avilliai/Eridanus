# coding=utf-8
import json,os
import time
import urllib

from run.acg_infromation.service.majsoul.majsoul_info.majsoul_Spider import selectInfo, select_triInfo, \
    select_triRecord, selectRecord

FILE_PATH = os.path.dirname(os.path.dirname(__file__))
#print(FILE_PATH)

def chooseID(IDdata):
    message = ""
    for i in range(0,len(IDdata)):
        message = message + "【" + str(i+1) + "】"+str(IDdata[i]["nickname"])+"("+judgeLevel(str(IDdata[i]["level"]["id"]))+")\n"
    message = message + "若列表内没有您要找的昵称，请将昵称补全以便于查找"
    return message


def printBasicInfo(IDdata,room_level,num):
    message = ""
    message = message + "昵称：" + str(IDdata["nickname"])+"  "

    score = int(IDdata["level"]["score"])+int(IDdata["level"]["delta"])
    message = message + processLevelInfo(score,str(IDdata["level"]["id"]))
    if num == "4":
        data_list = selectInfo(IDdata["id"],room_level)
        room = "四"
    else:
        data_list = select_triInfo(IDdata["id"], room_level)
        room = "三"
    if isinstance(data_list[0], urllib.error.URLError):
        message = message + "\n没有查询到在" + room + "人南的对局数据呢~\n"
    else:
        message = message + processBasicInfo(data_list[0], room_level, room + "人南",num)+"\n"
    if isinstance(data_list[2], urllib.error.URLError):
        message = message + "\n没有查询到在" + room + "人东的对局数据呢~\n"
    else:
        message = message + processBasicInfo(data_list[2], room_level, room + "人东",num)+"\n"
    message += 'PS：本数据不包含金之间以下对局以及2019.11.29之前的对局\n'
    return message


def printExtendInfo(IDdata,room_level,num):
    message = ""
    message = message + "昵称：" + str(IDdata["nickname"]) + "  "
    score = int(IDdata["level"]["score"]) + int(IDdata["level"]["delta"])
    message = message + processLevelInfo(score, str(IDdata["level"]["id"]))
    if num == "4":
        data_list = selectInfo(IDdata["id"],room_level)
        room = "四"
    else:
        data_list = select_triInfo(IDdata["id"], room_level)
        room = "三"
    if isinstance(data_list[0], urllib.error.URLError):
        message = message + "\n没有查询到在"+ judgeRoom(room_level) + room + "人南的对局数据呢~\n"
    else:
        message = message + processBasicInfo(data_list[0], room_level, room +"人南",num)
        message = message + processExtendInfo(data_list[1], room_level, room +"人南")
    if isinstance(data_list[2], urllib.error.URLError):
        message = message + "\n没有查询到在"+ judgeRoom(room_level) + room +"人东的对局数据呢~\n"
    else:
        message = message + processBasicInfo(data_list[2], room_level, room +"人东",num)
        message = message + processExtendInfo(data_list[3], room_level, room +"人东")
    message += 'PS：本数据不包含金之间以下对局以及2019.11.29之前的对局\n'
    return message

def printRecordInfo(IDdata,num):
    message = ""
    message = message + "昵称：" + str(IDdata["nickname"]) + "  "
    score = int(IDdata["level"]["score"]) + int(IDdata["level"]["delta"])
    message = message + processLevelInfo(score, str(IDdata["level"]["id"]))
    if num == 3:
        record = select_triRecord(IDdata["id"])
    elif num == 4:
        record = selectRecord(IDdata["id"])
    if isinstance(record, urllib.error.URLError):
        message = message + "没有查询到在该玩家近期的对局数据呢~\n"
    else:
        message = message + processRecordInfo(record,num)
    message += 'PS：本数据不包含金之间以下对局以及2019.11.29之前的对局\n'
    return message

def processExtendInfo(info,room_level,sessions):
    data = json.loads(info)
    message = "\n【" + judgeRoom(room_level)+ sessions + "进阶数据】\n"
    message = message + "和牌率：" + str(round(float(removeNull(data["和牌率"]))*100,2)) + "%  "
    message = message + "自摸率：" + str(round(float(removeNull(data["自摸率"]))*100,2)) + "%  "
    message = message + "默听率：" + str(round(float(removeNull(data["默听率"]))*100,2)) + "%  "
    message = message + "放铳率：" + str(round(float(removeNull(data["放铳率"]))*100,2)) + "%  \n"
    message = message + "副露率：" + str(round(float(removeNull(data["副露率"]))*100,2)) + "%  "
    message = message + "立直率：" + str(round(float(removeNull(data["立直率"]))*100,2)) + "%  "
    message = message + "流局率：" + str(round(float(removeNull(data["副露率"]))*100,2)) + "%  "
    message = message + "流听率：" + str(round(float(removeNull(data["流听率"]))*100,2)) + "%  \n"
    message = message + "一发率：" + str(round(float(removeNull(data["一发率"]))*100,2)) + "%  "
    message = message + "里宝率：" + str(round(float(removeNull(data["里宝率"]))*100,2)) + "%  "
    message = message + "先制率：" + str(round(float(removeNull(data["先制率"]))*100,2)) + "%  "
    message = message + "追立率：" + str(round(float(removeNull(data["追立率"]))*100,2)) + "%  \n"
    message = message + "平均打点：" + str(removeNull(data["平均打点"])) + "  "
    message = message + "平均铳点：" + str(removeNull(data["平均铳点"])) + "  "
    try:
        message = message + "最大连庄：" + str(removeNull(data["最大连庄"])) + "  "
    except:
        message = message + "最大连庄：0  "
    message = message + "和了巡数：" + str(round(float(removeNull(data["和了巡数"])),2)) + "  \n"
    return message

def processBasicInfo(info,room_level,sessions,num):
    data = json.loads(info)
    message = "\n【" + judgeRoom(room_level)+ sessions + "基础数据】\n"
    message = message + "总场次：" + str(data["count"])+"\n"
    message = message + "一位率：" + str(round(float(data["rank_rates"][0])*100,2)) + "%  "
    message = message + "二位率：" + str(round(float(data["rank_rates"][1])*100,2)) + "%  \n"
    message = message + "三位率：" + str(round(float(data["rank_rates"][2])*100,2)) + "%  "
    if num=="4":
        message = message + "四位率：" + str(round(float(data["rank_rates"][3])*100,2)) + "%"
    return message

def processLevelInfo(score,level):
    message = ""
    intlevel = int(level)
    if score < 0:
        if intlevel % 10 ==1:
            intlevel = intlevel-98
            level = str(intlevel)
        else:
            level = str(intlevel-1)
        score = level_start(level)
    elif score >= level_max(level):
        if intlevel % 10 == 3:
            intlevel = intlevel+98
            if intlevel == 10601 or intlevel == 20601:
                intlevel = intlevel + 100
            level = str(intlevel)
        else:
            level = str(intlevel+1)
        score = level_start(level)
    message = message + "当前段位：" + judgeLevel(level)+"  "
    if judgeLevel(level)[0:2] == "魂天":
        score = score / 100
    message = message + "当前pt数：" + str(score)+"\n"
    return message

def processRecordInfo(record,num):
    data = json.loads(record)
    message = "\n该玩家最近的对局信息如下：\n"
    if len(data) < 5:
        count = len(data)
    else:
        count = 5
    for i in range(0,count):
        message = message + "\n【" + str(i+1) + "】牌谱ID：" + str(data[i]["uuid"]) +"\n"
        for j in range(0,num):
            message = message + str(data[i]["players"][j]["nickname"]) + "(" + str(data[i]["players"][j]["score"])+")  "
        message = message + "\n"
        message = message + "Start：" + str(convertTime(data[i]["startTime"]))+"  "
        message = message + "End：" + str(convertTime(data[i]["endTime"]))+"  \n"
    return message

def judgeLevel(level):
    if level == "10203" or level == "20203": return "雀士三"
    elif level == "10301" or level == "20301": return "雀杰一"
    elif level == "10302" or level == "20302": return "雀杰二"
    elif level == "10303" or level == "20303": return "雀杰三"
    elif level == "10401" or level == "20401": return "雀豪一"
    elif level == "10402" or level == "20402": return "雀豪二"
    elif level == "10403" or level == "20403": return "雀豪三"
    elif level == "10501" or level == "20501": return "雀圣一"
    elif level == "10502" or level == "20502": return "雀圣二"
    elif level == "10503" or level == "20503": return "雀圣三"
    elif level[0:3] == "107" or level[0:3] == "207": return "魂天"+str(int(level[-2:]))

def judgeRoom(room_level):
    if room_level == "0": return "总体"
    elif room_level == "1": return "金之间"
    elif room_level == "2": return "玉之间"
    elif room_level == "3": return "王座之间"

def removeNull(data):
    if data == None:
        return "0"
    else:
        return data

def convertTime(datatime):
    timeArray = time.localtime(datatime)
    Time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return Time

def level_max(level):
    if level == "10203" or level == "20203": return 1000
    elif level == "10301" or level == "20301": return 1200
    elif level == "10302" or level == "20302": return 1400
    elif level == "10303" or level == "20303": return 2000
    elif level == "10401" or level == "20401": return 2800
    elif level == "10402" or level == "20402": return 3200
    elif level == "10403" or level == "20403": return 3600
    elif level == "10501" or level == "20501": return 4000
    elif level == "10502" or level == "20502": return 6000
    elif level == "10503" or level == "20503": return 9000
    elif level[0:3] == "107" or level[0:3] == "207": return 2000
    #elif level == "10601" or level == "20601": return 9999999

def level_start(level):
    if level == "10203" or level == "20203": return 500
    elif level == "10301" or level == "20301": return 600
    elif level == "10302" or level == "20302": return 700
    elif level == "10303" or level == "20303": return 1000
    elif level == "10401" or level == "20401": return 1400
    elif level == "10402" or level == "20402": return 1600
    elif level == "10403" or level == "20403": return 1800
    elif level == "10501" or level == "20501": return 2000
    elif level == "10502" or level == "20502": return 3000
    elif level == "10503" or level == "20503": return 4500
    elif level[0:3] == "107" or level[0:3] == "207": return 1000
    #elif level == "10601" or level == "20601": return 10000
