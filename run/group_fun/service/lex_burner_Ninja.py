import asyncio
import re

import httpx
from bs4 import BeautifulSoup

class Lexburner_Ninja:
    def __init__(self):
        self.name = "Lexburner_Ninja"
    async def query_ninjutsu(self,name):
        async with httpx.AsyncClient() as client:
            response=await client.get(f"https://wsfrs.com/?search={name}")
            html_content=response.text
            def parse_response(html_content):

                soup = BeautifulSoup(html_content, 'html.parser')
                jutsus_links = soup.find_all('a', href=lambda x: x and '/jutsus/' in x)
                base_url = 'https://wsfrs.com'
                full_urls = [base_url + link['href'] for link in jutsus_links]
                return full_urls[0]
            url=parse_response(html_content)
            response=await client.get(url)
            html_content=response.text
            return await self.parse_jutsu_details(html_content)
            #return parse_response(html_content)
    async def random_ninjutsu(self):
        async with httpx.AsyncClient() as client:
            url="https://wsfrs.com/api/jutsus?limit=1&sortBy=random"
            response = await client.get(url)
            data = response.json()
            return data['jutsus'][0]

    async def parse_jutsu_details(self,html_content):
        """
        解析忍术详情页面，提取标题、描述、标签、教学视频和关联忍术。

        Args:
            html_content (str): HTML 页面内容

        Returns:
            dict: 包含忍术信息的字典
        """
        # 创建 BeautifulSoup 对象
        soup = BeautifulSoup(html_content, 'html.parser')

        # 初始化结果字典
        result = {
            "title": "",
            "description": "",
            "tags": [],
            "video_link": "",
            "related_jutsus": []
        }

        # 1. 提取忍术标题
        title_element = soup.find('h2', string=re.compile(r'.+'))  # 查找第一个非空 h2
        result['title'] = title_element.text.strip() if title_element else "未找到标题"

        # 2. 提取忍术描述
        description_section = soup.find('h3', string='忍术描述')
        if description_section:
            description_container = description_section.find_next('div', class_=re.compile(r'bg-gray-50'))
            description_element = description_container.find('p') if description_container else None
            result['description'] = description_element.text.strip() if description_element else "未找到描述"
        else:
            result['description'] = "未找到描述"

        # 3. 提取忍术标签
        tags_section = soup.find('h3', string='忍术标签')
        if tags_section:
            tags_container = tags_section.find_next('div', class_=re.compile(r'bg-gray-50'))
            if tags_container:
                tags = tags_container.find_all('button')  # 假设标签在 button 元素中
                result['tags'] = [tag.text.strip() for tag in tags]
            else:
                result['tags'] = []
        else:
            result['tags'] = []

        # 4. 提取教学视频
        video_section = soup.find('h3', string='教学视频')
        if video_section:
            video_container = video_section.find_next('div', class_=re.compile(r'bg-gray-50'))
            video_link_element = video_container.find('a', href=lambda
                x: x and 'bilibili.com' in x) if video_container else None
            result['video_link'] = video_link_element['href'] if video_link_element else "未找到视频链接"
        else:
            result['video_link'] = "未找到视频链接"

        # 5. 提取关联忍术
        related_section = soup.find('h3', string='强于的忍术')
        if related_section:
            related_container = related_section.find_next('div', class_=re.compile(r'bg-gray-50'))
            if related_container:
                related_jutsus = related_container.find_all('li')
                for jutsu in related_jutsus:
                    link = jutsu.find('a')
                    if link:
                        name = link.contents[0].strip()  # 获取忍术名称
                        # 查找括号内的标签，假设在 <span> 中且包含括号
                        tag_element = link.find('span')
                        tag = tag_element.text.strip('()') if tag_element and tag_element.text.startswith(
                            '(') else "未知标签"
                        url = 'https://wsfrs.com' + link['href']
                        result['related_jutsus'].append({
                            "name": name,
                            "tag": tag,
                            "url": url
                        })
            else:
                result['related_jutsus'] = []
        else:
            result['related_jutsus'] = []

        return result