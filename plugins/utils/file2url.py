import httpx

# 设置代理（如果需要）
proxies = {
    "http://": "http://127.0.0.1:10809",
    "https://": "http://127.0.0.1:10809",
}

# 请求的 URL
url = "https://up.ly93.cc/upload/token"

# 请求头
headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://up.ly93.cc",
    "Referer": "https://up.ly93.cc/",
    "Sec-CH-UA": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "Sec-CH-UA-Mobile": "?0",
    "Sec-CH-UA-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    "X-Requested-With": "XMLHttpRequest",
}

# 请求体数据
data = {
    # 填入实际需要的键值对
    "name": "fsfsaf.mp3"
}

# 发起请求
with httpx.Client(proxies=proxies) as client:
    response = client.post(url, headers=headers, data=data)

# 输出响应
print("状态代码:", response.status_code)
print("响应内容:", response.text)
