# coding=utf-8
from bs4 import BeautifulSoup
import urllib.request
import urllib.error
import urllib.parse
import json
import time

baseurl = "https://ak-data-1.sapk.ch/api/v2/pl4"
tribaseurl = "https://ak-data-1.sapk.ch/api/v2/pl3"


def getURL(url):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    }
    try:
        response = urllib.request.Request(url=url, headers=headers, method="GET")
        req = urllib.request.urlopen(response,timeout=3)
        info = str(BeautifulSoup(req.read().decode('utf-8'), "html.parser"))
    except urllib.error.URLError as e:
        return e
    return info

def getID(nickname):#获取牌谱屋角色ID
    nickname = urllib.parse.quote(nickname) #UrlEncode转换
    url = baseurl + "/search_player/"+nickname+"?limit=9"
    data = getURL(url)
    if isinstance(data,urllib.error.URLError):
        return -404
    datalist = json.loads(data)
    #print(datalist)
    if datalist == [] :
        return -1
    return datalist

def gettriID(nickname):
    nickname = urllib.parse.quote(nickname) #UrlEncode转换
    url = tribaseurl + "/search_player/"+nickname+"?limit=9"
    data = getURL(url)
    if isinstance(data,urllib.error.URLError):
        return -404
    datalist = json.loads(data)
    if datalist == [] :
        return -1
    return datalist


def selectLevel(room_level):
    level_list = []
    if room_level == "0":
        level_list.append("16.12.9")#所有南场信息
        level_list.append("15.11.8")#所有东场信息
    elif room_level == "1":
        level_list.append("9")#金南
        level_list.append("8")#金东
    elif room_level == "2":
        level_list.append("12")#玉南
        level_list.append("11")#玉东
    elif room_level == "3":
        level_list.append("16")#王座南
        level_list.append("15")#王座东
    return level_list

def select_triLevel(room_level):
    level_list = []
    if room_level == "0":
        level_list.append("22.24.26")#所有南场信息
        level_list.append("21.23.25")#所有东场信息
    elif room_level == "1":
        level_list.append("22")#金南
        level_list.append("21")#金东
    elif room_level == "2":
        level_list.append("24")#玉南
        level_list.append("23")#玉东
    elif room_level == "3":
        level_list.append("26")#王座南
        level_list.append("25")#王座东
    return level_list

def select_triInfo(id,room_level): #信息查询
    localtime = time.time()
    urltime = str(int(localtime*1000)) #时间戳
    basicurl = tribaseurl+"/player_stats/"+str(id)+"/1262304000000/"+urltime+"?mode="
    extendurl = tribaseurl+"/player_extended_stats/"+str(id)+"/1262304000000/"+urltime+"?mode="
    data_list = []
    level_list = select_triLevel(room_level)
    for i in range(0,2):
        data_list.append(getURL(basicurl + level_list[i]))
        data_list.append(getURL(extendurl + level_list[i]))
    return data_list


def selectInfo(id,room_level): #信息查询
    localtime = time.time()
    urltime = str(int(localtime*1000)) #时间戳
    basicurl = baseurl+"/player_stats/"+str(id)+"/1262304000000/"+urltime+"?mode="
    extendurl = baseurl+"/player_extended_stats/"+str(id)+"/1262304000000/"+urltime+"?mode="
    data_list = []
    level_list = selectLevel(room_level)
    for i in range(0,2):
        data_list.append(getURL(basicurl + level_list[i]))
        data_list.append(getURL(extendurl + level_list[i]))
    return data_list

def selectRecord(id):
    localtime = time.time()
    urltime = str(int(localtime * 1000))  # 时间戳
    basicurl = baseurl + "/player_stats/" + str(id) + "/1262304000000/" + urltime + "?mode=16.12.9.15.11.8"
    count = str(json.loads(getURL(basicurl))["count"])
    recordurl = baseurl + "/player_records/"+str(id)+"/"+urltime+"/1262304000000?limit=5&mode=16.12.9.15.11.8&descending=true&tag="+count
    record = getURL(recordurl)
    return record

def select_triRecord(id):
    localtime = time.time()
    urltime = str(int(localtime * 1000))  # 时间戳
    basicurl = tribaseurl + "/player_stats/" + str(id) + "/1262304000000/" + urltime + "?mode=22.24.26.21.23.25"
    count = str(json.loads(getURL(basicurl))["count"])
    recordurl = tribaseurl + "/player_records/"+str(id)+"/"+urltime+"/1262304000000?limit=5&mode=22.24.26.21.23.25&descending=true&tag="+count
    record = getURL(recordurl)
    return record
