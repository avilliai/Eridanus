import json
import requests
import httpx
import asyncio
import datetime


async def claendar_bangumi_get_json():
    async with httpx.AsyncClient() as client:
        url = "https://api.bgm.tv/calendar"
        response = await client.get(url)
        if response.status_code:
            data = response.json()
            weekday = datetime.datetime.today().weekday()
            week=data[weekday]['weekday']['cn']
            calendar_json_init=data[weekday]['items']
            #print(week)
            #print(json.dumps(data, indent=4))
        return calendar_json_init,week

async def bangumi_subject_post_json(type=None,target=None):
    async with httpx.AsyncClient() as client:
        if type is not None:
            params = {
                "type": type,
            }
        else:
            params = {}
        try:
            url = f"https://api.bgm.tv/search/subject/{target}"
            response = await client.post(url, params=params)
            if response.status_code:
                data = response.json()
                #print(data)
                #print(json.dumps(data, indent=4))
            return data
        except Exception as e:
            return False

async def bangumi_subjects_get_json_PIL(subject_id=None):
    async with httpx.AsyncClient() as client:

        try:
            url = f"https://api.bgm.tv/v0/subjects/{subject_id}"
            response = await client.get(url)
            if response.status_code:
                data = response.json()
                #print(data)
                #print(json.dumps(data, indent=4))
                #print(data["summary"])
                contents_other=''
                for subject in data['infobox']:
                    if subject['key'] == "放送星期":
                        week_fang=subject['value']
                    elif subject['key'] == "话数":
                        week_jishu=subject['value']
                    if subject['key'] not in {'中文名','放送开始','放送星期','别名'}:
                        contents_other+=f'·{subject["key"]}：{subject["value"]}\n'
                img_url=data["images"]['large']
                name_bangumi = data['name_cn']
                if '' == name_bangumi:
                    name_bangumi = data['name']
                if 'rating' in data:
                    score=data['rating']['score']
                contents=[]
                text=f"{name_bangumi}\n"
                contents.append(f"title:{name_bangumi}({score}☆)")
                contents.append(f"播出日期：{data['date']} | {week_fang}放送 | {week_jishu}话\n简介：\n{data['summary']}")
                tags='tag:'
                for tag in data['tags']:
                    tags+=f"#{tag['name']}# "
                if tags!='tag:':
                    contents.append(f"{tags}")


            return contents,img_url,contents_other
        except Exception as e:
            return False



async def main():
    #data = await bangumi_subject_post_json(target='败犬女主太多了',type=2)
    calendar_json_init,week=await claendar_bangumi_get_json()
    print(week)
    print(json.dumps(calendar_json_init, indent=4))

# 运行异步任务
if __name__ == "__main__":
    asyncio.run(main())