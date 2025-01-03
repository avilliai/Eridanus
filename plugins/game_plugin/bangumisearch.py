from bs4 import BeautifulSoup
import httpx
import random
def get_headers():
    user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"]

    userAgent = random.choice(user_agent_list)
    headers = {'User-Agent': userAgent}
    return headers
async def banguimiList(year, month, top):
    rank = 1  # 排名
    page = 1  # 页数
    finNal_Cover = []
    fiNal_Text = []
    isbottom = 0  # 标记是否到底
    page = top // 24  # 计算页数
    if top % 24 != 0:
        page += 1  # 向上取整
    for i in range(1, page + 1):
        url = f"https://bgm.tv/anime/browser/airtime/{year}-{month}?sort=rank&page={i}"  # 构造请求网址，page参数为第i页
        async with httpx.AsyncClient(timeout=20, headers=get_headers()) as client:  # 100s超时
            response = await client.get(url)  # 发起请求
        soup = BeautifulSoup(response.content, "html.parser")
        name_list = soup.find_all("h3")  # 获取番剧名称列表
        score_list = soup.find_all("small", class_="fade")  # 获取番剧评分列表
        popularity_list = soup.find_all("span", class_="tip_j")  # 获取番剧评分人数列表)
        anime_items = soup.find_all("img", class_="cover")

        for iCover in anime_items:
            src_value = str(iCover).split('src="')[1].split('"')[0]
            # 自动补全https前缀
            src_url = f"https:{src_value}"
            finNal_Cover.append(src_url)

        for j in range(len(score_list)):
            try:
                name_jp = name_list[j].find("small", class_="grey").string + "\n    "  # 获取番剧日文名称
            except:
                name_jp = ""
            name_ch = name_list[j].find("a", class_="l").string  # 获取番剧中文名称
            score = score_list[j].string  # 获取番剧评分
            popularity = popularity_list[j].string  # 获取番剧评分人数
            fiNal_Text.append("{:<3}".format(rank) + f"{name_jp}{name_ch}\n    {score}☆  {popularity}\n")
            if rank == top:  # 达到显示上限
                break
            rank += 1
        if rank % 24 != 1 and rank < top:  # 到底了
            isbottom = 1
            break
    return fiNal_Text, finNal_Cover, isbottom


async def bangumisearch(url):
    async with httpx.AsyncClient(timeout=20, headers=get_headers()) as client:  # 100s超时
        response = await client.get(url)  # 发起请求
    soup = BeautifulSoup(response.content, "html.parser")
    subjectlist = soup.find_all("h3")[0:-2]
    crtlist = soup.find_all("h3")[-2].find_all("dd")
    if len(crtlist) == 0:
        subjectlist = soup.find_all("h3")[0:-3]
        crtlist = soup.find_all("h3")[-3].find_all("dd")
    str0 = soup.find("title").string + "\n"
    for i in range(len(subjectlist)):
        str0 += f"{i + 1}.{subjectlist[i].find('a').string}\n"
    str0 += "相关人物：\n"
    for j in range(len(crtlist)):
        str0 += f"0{j + 1}.{crtlist[j].string}\n"
    list = [str0, subjectlist, crtlist]
    return list


async def screenshot_to_pdf_and_png(url, path, width=1024, height=9680):
    url = f"https://mini.s-shot.ru/{width}x{height}/PNG/1800/?{url}"
    async with httpx.AsyncClient(timeout=200) as client:
        r = await client.get(url)
        with open(path, "wb") as f:
            f.write(r.content)
        return path


async def delete_msg_async(msg_id):
    url = "http://localhost:3000/delete_msg"
    payload = {
        "message_id": str(msg_id)
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ff'
    }
    async with httpx.AsyncClient(timeout=None, headers=headers) as client:
        response = await client.post(url, json=payload)