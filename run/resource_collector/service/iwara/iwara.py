
# -*- coding: utf-8 -*-

import datetime
import os
import random
import requests
import time

from cffi.backend_ctypes import unicode

USER_INFO = [
    # {
    #   "user_name": The name of iwara user,
    #   "file_prefix": Add a prefix for all video files if needed,
    #   "download_index": Download the video by index in this list only. Leave it blank for all
    # }
    {"user_name": "Forget Skyrim.", "profile_name": "forgetskyrim", "file_prefix": "Forget Skyrim"},
    {"user_name": "嫖阿姨", "profile_name": "user798290", "file_prefix": "P嫖阿姨"},
    {"user_name": "491033063", "file_prefix": "S神经觉醒"},
    {"user_name": "和颐雪", "profile_name": "user787392", "file_prefix": "H和颐雪"},
    # {"user_name": "miraclegenesismmd", "file_prefix": "MiracleGenesisMMD"},
    {"user_name": "嫚迷GirlFans", "profile_name": "girlfans", "file_prefix": "M嫚迷GirlFans"},
    {"user_name": "JUSWE", "file_prefix": "AlZ"},
    # {"user_name": "三仁月饼", "file_prefix": "S三仁月饼"},
    # {"user_name": "LTDEND", "file_prefix": ""},
    # {"user_name": "Mister Pink", "file_prefix": ""},
    # {"user_name": "qimiaotianshi", "file_prefix": ""},
    # {"user_name": "jvmpdark", "file_prefix": ""},
    # {"user_name": "EcchiFuta", "file_prefix": ""},
    {"user_name": "水水..", "profile_name": "user937858", "file_prefix": "S水水.."},
    # {"user_name": "慕光", "file_prefix": "M慕光"},
    {"user_name": "煜喵", "profile_name": "user1107866", "file_prefix": "Y煜喵"},
    # {"user_name": "113458", "file_prefix": "Y113458"},
    {"user_name": "腿 玩 年", "profile_name": "user221116", "file_prefix": "T腿玩年"},
    # {"user_name": "sugokunemui", "file_prefix": "sugokunemui"},
    # {"user_name": "mister-pink", "file_prefix": "mister-pink"},
    {"user_name": "二两牛肉面jd", "profile_name": "user178752", "file_prefix": "E二两牛肉面"},
    # {"user_name": "hisen", "file_prefix": "Hisen"},
    {"user_name": "MMD_je", "profile_name": "mmdje", "file_prefix": "mmdje"},
    {"user_name": "emisa", "file_prefix": ""},
    {"user_name": "穴儿湿袭之", "profile_name": "user1235858", "file_prefix": "S穴儿湿袭之"},
    {"user_name": "SEALING", "file_prefix": ""},
    {"user_name": "icegreentea", "file_prefix": ""},
    {"user_name": "NekoSugar", "file_prefix": ""},
]

PROXIES = {
    "https": "http://127.0.0.1:8080",
}

DATE_LIMIT = 14


def main(user_name, file_prefix, profile_name=None):
    if profile_name is not None:
        user_api = "https://api.iwara.tv/profile/{}".format(requests.utils.quote(profile_name))
        print("{} https://www.iwara.tv/profile/{}".format(user_name, profile_name))
    else:
        user_api = "https://api.iwara.tv/profile/{}".format(requests.utils.quote(user_name))
        print("{} https://www.iwara.tv/profile/{}".format(user_name, user_name))
    user_api_req = requests.get(user_api, proxies=PROXIES)
    while user_api_req.status_code not in [200]:
        print("profile_api", user_api_req.status_code)
        time.sleep(random.randint(1, 5))
        user_api_req = requests.get(user_api, proxies=PROXIES)
    if "message" in user_api_req.json() and user_api_req.json()["message"] == "errors.notFound":
        search_api = "https://api.iwara.tv/search"
        search_api_req = requests.get(search_api, params={
            "type": "user",
            "query": user_name,
            "page": 0,
        }, proxies=PROXIES)
        if len(search_api_req.json()["results"]) == 0:
            print("user not found")
            print("-" * 80)
            return
        id_like_username = search_api_req.json()["results"][0]["username"]
        print("{} https://www.iwara.tv/profile/{}".format(user_name, id_like_username))
        user_api = "https://api.iwara.tv/profile/{}".format(requests.utils.quote(id_like_username))
        user_api_req = requests.get(user_api, proxies=PROXIES)
    user_id = user_api_req.json()["user"]["id"]

    video_list = list()
    page = 0
    count = 0
    limit = 32
    while page * limit <= count:
        video_api = "https://api.iwara.tv/videos"
        video_api_req = requests.get(video_api, params={
            "user": user_id,
            "sort": "date",
            "page": page,
        }, proxies=PROXIES)
        if video_api_req.status_code not in [200]:
            print(video_api_req.status_code)
            time.sleep(random.randint(1, 5))
            continue
        count = video_api_req.json()["count"]
        for item in video_api_req.json()["results"]:
            if item["slug"] is not None:
                video_url = "https://www.iwara.tv/video/{}/{}".format(item["id"], item["slug"])
            else:
                video_url = "https://www.iwara.tv/video/{}".format(item["id"])
            video_list.append((
                video_url,
                item["title"],
                # datetime.datetime.strptime(item["updatedAt"], "%Y-%m-%dT%H:%M:%S.%fZ"),
                datetime.datetime.strptime(item["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ"),
            ))
        page += 1
        # print page, limit, page * limit, count

    video_list.reverse()
    for i, video in enumerate(video_list):
        _file_prefix = u"{}.{:03d}.".format(
            file_prefix.decode("utf-8") if file_prefix != "" else user_name.decode("utf-8"),
            i + 1,
        )
        _file_name = u"{}.mp4".format(
            unicode(video[1]).replace("/", " ").replace("?", " ").replace("*", " "),
        )
        if video[2] >= datetime.datetime.now() - datetime.timedelta(days=DATE_LIMIT):
            print(u"{}\n{} {} {}".format(
                _file_prefix + _file_name,
                "[Downloaded]" if os.path.isfile(_file_prefix + _file_name) else "",
                video[0],
                video[2],
            ))
        video_list[i] += (i + 1,)
    print("-" * 80)


if __name__ == "__main__":
    USER_INFO.reverse()
    for user in USER_INFO:
        main(
            user["user_name"],
            user["file_prefix"],
            user["profile_name"] if "profile_name" in user else None,
        )
        time.sleep(3)

