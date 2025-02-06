import httpx
import asyncio
from bs4 import BeautifulSoup
import re
import time

async def fetch_url(url, headers):
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        return response.text

def extract_div_contents(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    result_op_divs = soup.find_all('div', class_='result-op c-container new-pmd')
    result_xpath_log_divs = soup.find_all('div', class_='result c-container xpath-log new-pmd')
    
    entries = []
    
    for div in result_op_divs + result_xpath_log_divs:
        title_tag = div.find('h3')
        title = title_tag.get_text(strip=True) if title_tag else "无标题"
        link_tag = div.find('a', href=True)
        link = link_tag['href'] if link_tag else "无链接"
        
        all_texts = [text for text in div.stripped_strings if text != title]
        content = ' '.join(all_texts)
        
        content = re.sub(r'UTC\+8(\d{5}:\d{2}:\d{2})', lambda x: 'UTC+8 ' + ':'.join([x.group(1)[i:i+2] for i in range(0, len(x.group(1)), 2)]).lstrip(':'), content)
        content = re.sub(r'(\d{2}:\d{2})(\d{4}-\d{2}-\d{2})', r'\1 \2', content)
        content = re.sub(r'(\d{2}) (\d{2}) : (\d{2}) (\d{2}) : (\d{2}) (\d{2})', r'\1:\3:\5', content)
        
        entries.append({
            'title': title,
            'link': link,
            'content': content
        })
    
    return entries

async def baidu_search(query):
    current_timestamp = int(time.time())
    url = f"https://www.baidu.com/s?wd={query}"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "identity",  # Request uncompressed content
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Connection": "keep-alive",
        "Cookie": "BAIDUID_BFESS=A66237379B97E6A261B58CF57A599B36:FG=1; BAIDU_WISE_UID=wapp_1735376969138_24; ZFY=SAnc8iRNM:ANXuj2oLMz5qIRu8biHnpXnJWjpW7TDpqQ:C; __bid_n=19411378e1092166a470ad; BDUSS=hrYmdrV3J6YURhcXNVdmhEdzl6R285cXlUOEUxTjljVThOZFlPdkt1ck1PTHhuSVFBQUFBJCQAAAAAAAAAAAEAAAC8k8VDx-W0v7XE0MfQxzIwMDkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMynlGfMp5RnWm; BDUSS_BFESS=hrYmdrV3J6YURhcXNVdmhEdzl6R285cXlUOEUxTjljVThOZFlPdkt1ck1PTHhuSVFBQUFBJCQAAAAAAAAAAAEAAAC8k8VDx-W0v7XE0MfQxzIwMDkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMynlGfMp5RnWm; RT=\"z=1&dm=baidu.com&si=67fe5ea0-9903-498c-8a2c-caac8abb3423&ss=m6rr8uo8&sl=2&tt=6lh&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf&ld=6js&ul=82y&hd=838\"; BIDUPSID=A66237379B97E6A261B58CF57A599B36; PSTM=1738765634; BDRCVFR[BIVAaPonX6T]=-_EV5wtlMr0mh-8uz4WUvY; H_PS_PSSID=61027_61672_61987; BD_UPN=12314753; BA_HECTOR=ak0h04a58k80a0a1a42h00a08krj591jq6ta41v; delPer=0; BD_CK_SAM=1; PSINO=3; BDORZ=FFFB88E999055A3F8A630C64834BD6D0; channel=bing; baikeVisitId=ed9be3e1-1a99-40db-ba9e-5fb15086499e; sugstore=1; H_PS_645EC=b0c8DXwu1zardcmOPhN4OqPWlhNdg5njr4BBu4r%2FG3omWhcYKkp9EBJovo73j%2BCbdzDizw7sKluo",
        "DNT": "1",
        "Host": "www.baidu.com",
        "Referer": "https://www.baidu.com/s?wd=%E6%97%B6%E9%97%B4&base_query=%E6%97%B6%E9%97%B4&pn=0&oq=%E6%97%B6%E9%97%B4&tn=68018901_58_oem_dg&ie=utf-8&usm=4&rsv_idx=2&rsv_pq=db1e11ba0149dd28&rsv_t=051f4Gfs0d6O1kjBloAcKUq0VT1U06iWRPu%2FNeyVIvZiNPdxDgnaeJjnszjKZFtGWofQv4iUGorN",
        "Sec-Ch-Ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Microsoft Edge\";v=\"132\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
        "X-Custom-Time": str(current_timestamp),
    }
    
    html_content = await fetch_url(url, headers)
    entries = extract_div_contents(html_content)
    
    output = "baidu搜索结果:\n"
    for entry in entries:
        output += f"标题: {entry['title']}\n"
        output += f"链接: {entry['link']}\n"
        output += f"内容: {entry['content']}\n"
        output += "-" * 20 + "\n"
    
    return output

async def searx_search(query):
    url = 'https://searx.bndkt.io/search'
    current_timestamp = int(time.time())
    params = {
        'q': query,
        'categories': 'general',
        'language': 'zh-CN',
        'time_range': '',
        'safesearch': '0',
        'theme': 'simple'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0',
        'Accept': '*/*',
        "X-Custom-Time": str(current_timestamp),
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            articles = soup.find_all('article', class_='result result-default category-general')
            
            results = []
            for article in articles:
                title = article.find('h3').get_text(strip=True)
                link = article.find('a', class_='url_header')['href']
                content = article.find('p', class_='content').get_text(strip=True)
                results.append(f"标题: {title}\n链接: {link}\n内容: {content}\n{'-'* 20}")

            final = "searx搜索结果:\n" + "\n".join(results)
            return final
        except httpx.HTTPStatusError as exc:
            print(f"An HTTP error occurred: {exc}")
            print(exc.response.text)
        except httpx.RequestError as exc:
            print(f"An error occurred while making the request: {exc}")