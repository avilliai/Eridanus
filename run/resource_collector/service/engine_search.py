import httpx
import asyncio
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import urljoin, quote, unquote

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
        output += "- " * 10 + "\n"
    
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
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": "_pk_id.3.9c95=99d38b3e33bd1ecf.1738772334.; _pk_ses.3.9c95=1",
        "DNT": "1",
        "Host": "searx.bndkt.io",
        "Origin": "null",
        "Sec-Ch-Ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Microsoft Edge\";v=\"132\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
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
                results.append(f"标题: {title}\n链接: {link}\n内容: {content}\n{'- '* 10}")

            final = "searx搜索结果:\n" + "\n".join(results)
            return final
        except httpx.HTTPStatusError as exc:
            print(f"An HTTP error occurred: {exc}")
            print(exc.response.text)
        except httpx.RequestError as exc:
            print(f"An error occurred while making the request: {exc}")


async def html_read(url, config = None):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Cache-Control": "max-age=0",
        "DNT": "1",
        "Priority": "u=0, i",
        "Referer": "https://github.com/",
        "Sec-Ch-Ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Microsoft Edge\";v=\"132\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0"
    }
    if config is not None and config.common_config.basic_config["proxy"]["http_proxy"]:
        proxies = {"http://": config.common_config.basic_config["proxy"]["http_proxy"], "https://": config.common_config.basic_config["proxy"]["http_proxy"]}
    else:
        proxies = None
    #proxies = {"http://" : "http://127.0.0.1:7890", "https://" : "http://127.0.0.1:7890"}
    
    decoded_url = unquote(url)
    parsed_url = httpx.URL(decoded_url)
    encoded_path = quote(parsed_url.path)
    encoded_url = str(parsed_url.copy_with(path=encoded_path))
    
    async with httpx.AsyncClient(follow_redirects=True, timeout=None, proxies=proxies, headers=headers) as client:
        try:
            response = await client.get(encoded_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            if not soup.html:
                print("未找到<html>标签，请确认网页内容是否正确加载。")
                return "未找到<html>标签，请确认网页内容是否正确加载。"
            
            for script_or_style in soup(['script', 'style']):
                script_or_style.decompose()

            url_attributes = {
                'a': 'href',
                'img': 'src',
                'link': 'href',
                'iframe': 'src',
            }

            def recurse(node, level=0):
                indent = '  ' * level
                result = []
                
                if hasattr(node, 'name') and node.name is not None:
                    tag_name = node.name.lower()
                    
                    if tag_name in ['script', 'style']:
                        return result
                    
                    if tag_name == 'pre' or tag_name == 'code':
                        all_lines = []
                        # 检查是否有直接的`<span>`子元素
                        spans = node.find_all('span', recursive=False)
                        if spans:
                            for span in spans:
                                # 获取每个span的所有子孙节点的文本，并保持其中的空白字符
                                line_parts = [part.get_text() if hasattr(part, "get_text") else str(part) for part in span.contents]
                                full_line = ''.join(line_parts)

                                # 如果行中只包含空白字符，也添加到all_lines中
                                stripped_line = full_line.strip()
                                if stripped_line or (full_line and not full_line.isspace()):
                                    all_lines.append(full_line)
                        else:
                            # 如果没有`<span>`子元素，则直接使用`<code>`标签内的文本，并保持其中的空白字符
                            code_text = node.get_text()
                            lines = code_text.split('\n')
                            for line in lines:
                                stripped_line = line.strip()
                                if stripped_line or (line and not line.isspace()):
                                    all_lines.append(line)

                        formatted_code = "\n".join([f"{indent}{line}" for line in all_lines])
                        result.append(f"{indent}```yaml\n{formatted_code}\n{indent}```")
                        return result
                    
                    if tag_name in url_attributes:
                        attr = url_attributes[tag_name]
                        url_attr_value = node.get(attr, '')
                        
                        if tag_name == 'a' and url_attr_value.lower().startswith('javascript:'):
                            return result
                        
                        full_url = urljoin(str(response.url), url_attr_value)
                        if tag_name == 'a':
                            img_tag = node.find('img')
                            if img_tag:
                                alt = img_tag.get('alt', 'No description')
                                result.append(f"{indent}[{alt}]({full_url})")
                            else:
                                link_text = ' '.join(node.stripped_strings)
                                result.append(f"{indent}[{link_text}]({full_url})")
                        elif tag_name == 'img':
                            alt = node.get('alt', 'No description')
                            result.append(f"{indent}[{alt}]({full_url})")
                        else:
                            result.append(f"{indent}[URL]({full_url})")
                    else:
                        for child in node.children:
                            result.extend(recurse(child, level + 1))
                elif isinstance(node, str) and node.strip():
                    text = node.strip()
                    if text and not text.startswith("//<![CDATA[") and not text.endswith("//]]>"):
                        result.append(f"{indent}{text}")
                
                return result

            extracted_info = recurse(soup.html.body if soup.html and soup.html.body else soup.html)
            return "\n".join(extracted_info)
        except httpx.RequestError as e:
            #print(f"请求发生错误：{e}")
            return f"请求发生错误：{e}"

async def main():
    while True:
        url = input("请输入要测试的URL（或输入'exit'退出）：")
        if url.lower() == 'exit':
            break
        try:
            print(await html_read(url))
        except Exception as e:
            print(f"发生错误：{e}")

if __name__ == "__main__":
    asyncio.run(main())
