from asyncio import sleep

import requests
import os


async def Get_Access_Token():
    response = requests.post(f"https://www.ymgal.games/oauth/token?grant_type=client_credentials&client_id=ymgal&client_secret=luna0327&scope=public") #请求的url
    if response.status_code:
            #result = response.json()
        data = response.json()
    access_token = data["access_token"]
    return access_token

async def Get_Access_Token_json(access_token,url,params):
    #with httpx.AsyncClient() as client:
    headers = {
        'Accept': 'application/json;charset=utf-8',
        'Authorization': f'Bearer {access_token}',
        'version': '1'
    }
    response = requests.get(url, headers=headers,params=params)
    if response.status_code:
        data = response.json()
    return data

def flag_check(flag):#划定需要使用的方式
    if flag ==1:
        url='https://www.ymgal.games/open/archive/search-game'
        #print('精确游戏查询，flag=1')
        return url
    if flag ==2:
        url='https://www.ymgal.games/open/archive/search-game'
        #print('搜索游戏列表，flag=2')
        return url
    if flag ==3:
        url='https://www.ymgal.games/open/archive'
        #print('gid 查询单个游戏的详情，flag=3')
        return url
    if flag ==4:
        url='https://www.ymgal.games/open/archive'
        #print('orgId 查询机构详情，flag=4')
        return url
    if flag ==5:
        url='https://www.ymgal.games/open/archive'
        #print('cid 查询角色详情，flag=5')
        return url
    if flag ==6:
        url='https://www.ymgal.games/open/archive/game'
        #print('orgId 查询机构下的游戏，flag=6')
        return url
    if flag ==7:
        url='https://www.ymgal.games/open/archive/game'
        #print('查询日期区间内发行的游戏，flag=7')
        return url
    if flag ==8:
        url='https://www.ymgal.games/open/archive/random-game'
        #print('随机游戏，flag=8')
        return url
def params_check(flag,keyword=None,releaseStartDate=None,releaseEndDate=None):
    if flag ==1:
        params = {
            "mode": "accurate",
            "keyword": f"{keyword}",
            "similarity": "70"
        }
        return params
    if flag ==2:
        params = {
            "mode": "list",
            "keyword": f"{keyword}",
            "pageNum": "1",
            "pageSize": "20"
        }
        return params
    if flag ==3:
        params = {
            "gid": f"{keyword}"
        }
        return params
    if flag ==4:
        params = {
            "orgId": f"{keyword}"
        }
        return params
    if flag ==5:
        params = {
            "cid": f"{keyword}"
        }
        return params
    if flag ==6:
        params = {
            "orgId": f"{keyword}"
        }
        return params
    if flag ==7:
        params = {
            "releaseStartDate": f"{releaseStartDate}",
            "releaseEndDate": f"{releaseEndDate}"
        }
        return params
    if flag ==8:
        params = {
            "num": "1"
        }
        return params
async def get_game_image(url,filepath):
    if not os.path.exists(filepath):
        os.makedirs(filepath)

    response = requests.get(url)
    if response.status_code == 200:
        filename = url.split('/')[-1]
        #print(filename)
        img_path = os.path.join(filepath, filename)
        #print(img_path)
        files = os.listdir(filepath)
        if filename in files:
            #img_path = os.path.join(filepath, id)
            print(f'图片已存在，返回图片名称: {filename}')
            return img_path
        # 打开一个文件以二进制写入模式保存图片
        with open(img_path, 'wb') as f:
            f.write(response.content)
        print("图片已下载并保存为 {}".format(img_path))
        return img_path
    else:
        print(f"下载失败，状态码: {response.status_code}")
        return None
async def remove_game_image(file_path):
    if os.path.exists(file_path):
        await sleep(30)
        os.remove(file_path)
        print(f"文件 '{file_path}' 已删除。")
    else:
        print(f"文件 '{file_path}' 不存在。")
async def context_assemble(json_check):
    context=''
    if 'gid' in json_check:
        if 'name' in json_check:
            name = json_check['name']
            context += f"{name} | "
        if 'chineseName' in json_check:
            chineseName = json_check['chineseName']
            context += f"{chineseName}"
        context += f"\n"
        if 'gid' in json_check:
            gid = json_check['gid']
            context += f"gid:{gid} | "
        if 'haveChinese' in json_check:
            haveChinese = json_check['haveChinese']
            context += f"是否汉化：{haveChinese} | "
        if 'releaseDate' in json_check:
            releaseDate = json_check['releaseDate']
            context += f"发售日期：{releaseDate} | "
        if 'state' in json_check:
            state = json_check['state']
            context += f"state：{state} | "
        if 'mainName' in json_check:
            mainName = json_check['mainName']
            context += f"mainName：{mainName} | "
        if 'freeze' in json_check:
            freeze = json_check['freeze']
            context += f"标识状态：{freeze} | "
        return context
        pass
    else:
        if 'org' in json_check['data']:
            state_check='org'
        elif 'game' in json_check['data']:
            state_check='game'
        elif 'character' in json_check['data']:
            state_check='character'
        else:
            pass
        if 'org' in json_check['data'] or 'game' in json_check['data'] or 'character' in json_check['data']:
            if 'name' in json_check['data'][state_check]:
                name = json_check['data'][state_check]['name']
                context += f"{name} | "
            if 'chineseName' in json_check['data'][state_check]:
                chineseName = json_check['data'][state_check]['chineseName']
                context += f"{chineseName}"
            context += f"\n"
            if 'developerId' in json_check['data'][state_check]:
                developerId = json_check['data'][state_check]['developerId']
                developer_name = await developers_check(developerId)
                if developer_name:
                    context += f"开发商：{developer_name} | "
            if 'releaseDate' in json_check['data'][state_check]:
                releaseDate = json_check['data'][state_check]['releaseDate']
                context += f"发布时间：{releaseDate} | "
            if 'restricted' in json_check['data'][state_check]:
                restricted = json_check['data'][state_check]['restricted']
                context += f"限制级：{restricted} | "
            if 'state' in json_check['data'][state_check]:
                state = json_check['data'][state_check]['state']
                context += f"状态：{state} | "

            if 'country' in json_check['data'][state_check]:
                country_check = json_check['data'][state_check]['country']
                if country_check:
                    context += f"所属：{country_check} "

            if 'introduction' in json_check['data'][state_check]:
                introduction = json_check['data'][state_check]['introduction']
                context += f"\n"
                context += f"\n简介：{introduction}\n"
            context += f"\n"
            if 'developerId' in json_check['data'][state_check]:
                developerId = json_check['data'][state_check]['developerId']
                context += f"游戏品牌机构orgId：{developerId}\n"
            if 'orgId' in json_check['data'][state_check]:
                orgId_check = json_check['data'][state_check]['orgId']
                context += f"游戏品牌机构orgId：{orgId_check}\n"
            if 'haveChinese' in json_check['data'][state_check]:
                haveChinese = json_check['data'][state_check]['haveChinese']
                context += f"是否有中文：{haveChinese}\n"
            if 'gid' in json_check['data'][state_check]:
                gid = json_check['data'][state_check]['gid']
                context += f"游戏档案gid：{gid}\n"
            if 'website' in json_check["data"][state_check]:
                context += f"相关网址：\n"
                website_count = len(json_check["data"][state_check]["website"])
                for i in range(website_count):
                    if "title" in json_check['data'][state_check]['website'][i]:
                        link=json_check['data'][state_check]['website'][i]['link']
                        title = json_check['data'][state_check]['website'][i]['title']
                        context += f"{title}：{link}\n"
                        if "pid" in json_check['data'][state_check]['website'][i]:
                            pid = json_check['data'][state_check]['website'][i]['pid']
                            context += f"，PID：{pid}\n"
                    else:
                        continue
            if 'characters' in json_check["data"][state_check]:
                context += f"\n游戏角色：\n"
                characters_count = len(json_check["data"][state_check]["characters"])
                for i in range(characters_count):
                    if "cid" in json_check['data'][state_check]['characters'][i]:
                        cid = json_check['data'][state_check]['characters'][i]['cid']
                        characterPosition = json_check['data'][state_check]['characters'][i]['characterPosition']
                        if int(characterPosition) == 1:
                            characterPosition_check='男'
                        elif int(characterPosition) == 2:
                            characterPosition_check='女'
                        elif int(characterPosition) == 3:
                            characterPosition_check='扶她'
                        else:
                            characterPosition_check = '未知'

                        character_name = await character_check(cid)
                        if character_name:
                            #context += f"开发商：{developer_name}|"
                            if "cvId" in json_check['data'][state_check]['characters'][i]:
                                cvId = json_check['data'][state_check]['characters'][i]['cvId']
                                context += f"角色：{character_name}，cid：{cid}，CVid：{cvId}，性别：{characterPosition_check}\n"
                            else:
                                context += f"角色：{character_name}，cid：{cid}，性别：{characterPosition_check}\n"

                pass
            if 'staff' in json_check["data"][state_check]:
                context += f"\n"
                context += f"Staff职员表：\n"
                staff_count = len(json_check["data"][state_check]["staff"])
                for i in range(staff_count):
                    if "sid" in json_check['data'][state_check]['staff'][i]:
                        empName=json_check['data'][state_check]['staff'][i]['empName']
                        jobName = json_check['data'][state_check]['staff'][i]['jobName']
                        context += f"{jobName}：{empName}："
                        if "pid" in json_check['data'][state_check]['staff'][i]:
                            pid = json_check['data'][state_check]['staff'][i]['pid']
                            context += f"，PID：{pid}\n"
                    else:
                        continue



            if 'publishTime' in json_check['data'][state_check]:
                publishTime = json_check['data'][state_check]['publishTime']


    return context
async def developers_check(keyword):
    name=None
    flag = 4
    keyword = str(keyword)
    url = flag_check(flag)
    params = params_check(flag, keyword)
    access_token = await Get_Access_Token()
    json_check = await Get_Access_Token_json(access_token, url, params)
    #print(json_check)
    name = json_check['data']['org']['name']
    if 'chineseName' in json_check['data']['org']:
        name=json_check['data']['org']['chineseName']
    #print(name)
    return name
async def character_check(keyword):
    name = None
    flag = 5
    keyword = str(keyword)
    url = flag_check(flag)
    params = params_check(flag, keyword)
    access_token = await Get_Access_Token()
    json_check = await Get_Access_Token_json(access_token, url, params)
    #print(json_check)
    name = json_check['data']['character']['name']
    # print(name)
    return name
async def get_introduction(gid):
    introduction=''
    flag = 3
    keyword = str(gid)
    url = flag_check(flag)
    params = params_check(flag, keyword)
    access_token = await Get_Access_Token()
    json_check = await Get_Access_Token_json(access_token, url, params)
    #print(json_check)
    get_introduction = json_check['data']['game']['introduction']

    if 'developerId' in json_check['data']['game']:
        developerId = json_check['data']['game']['developerId']
        developer_name = await developers_check(developerId)
        if developer_name:
            introduction += f"开发商：{developer_name} \n"

    introduction += f'简介如下：{get_introduction}'
    #print(introduction)
    return introduction