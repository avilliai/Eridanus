import datetime
import json
from urllib.parse import quote

import httpx
import asyncio

from framework_common.utils.random_session_hash import random_session_hash


class ImageEditor:
    def __init__(self):
        self.upload_id = random_session_hash(10)

    async def upload_file(self, file_path):
        # 目标 URL
        url = "https://hidream-ai-hidream-e1-full.hf.space/gradio_api/upload?upload_id=q9t5khk69a"

        # 请求头
        headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "content-type": "multipart/form-data; boundary=----WebKitFormBoundaryekB8HJjRETFRKPP9",
            "origin": "https://hidream-ai-hidream-e1-full.hf.space",
            "priority": "u=1, i",
            "referer": "https://hidream-ai-hidream-e1-full.hf.space/?__theme=system",
            "sec-ch-ua": '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "sec-fetch-storage-access": "active",
            "user-agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0"
            ),
        }



        # 使用 httpx 异步客户端
        async with httpx.AsyncClient() as client:
            try:
                # 准备 multipart/form-data 数据
                files = {
                    "files": open(file_path, "rb"),  # 替换为实际文件名和文件流
                    "upload_id":self.upload_id,  # 添加 upload_id 作为表单字段
                }

                # 发送 POST 请求
                response = await client.post(url, headers=headers, files=files)

                # 检查响应状态
                if response.status_code == 200:
                    print("请求成功！")
                    print("响应内容:", response.text)
                    return response.json()[0]
                else:
                    print(f"请求失败，状态码: {response.status_code}")
                    print("响应内容:", response.text)

            except httpx.RequestError as e:
                print(f"请求发生错误: {e}")
            except FileNotFoundError:
                print("文件未找到，请检查文件路径是否正确")

    async def fetch_jwt(self):
        # 动态生成 expiration 参数（当前时间 + 5 分钟）
        expiration_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
        expiration_str = expiration_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        encoded_expiration = quote(expiration_str)  # URL 编码

        # 目标 URL
        url = (
            f"https://huggingface.co/api/spaces/HiDream-ai/HiDream-E1-Full/jwt"
            f"?expiration={encoded_expiration}&include_pro_status=true"
        )

        # 请求头
        headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "cookie": (
                "__stripe_mid=ad1bb1c6-a9b3-49ba-b230-ebc287a3ba7ec65671; "
                "__stripe_sid=a14969e3-e91f-4fcd-8041-fde14d03f467f465a6; "
                "token=TWWEibonthBukEjGERKLSXZzYNiFCJyonvWCfjiqOXJKqefXamIWVaGBakEpwJzamnNlXZZQnvVEbWztdPcgDfiXrtuveaxSNMSuhhqdrMgyCHGLfIyFLclzqKeAQNFL; "
                "datadome=Gysr_1H4c3Kk4ZluJJBPi9QBWsfo9_hRzTJClfQuSAFsc4EqXb71sWVIJFlVAWqbkGpTghS~FkRqjsqmzhBycDEJBZNKCIh0vX8q6lmxoZp4WAd_3ChYEGhHgXztYNX4; "
                "aws-waf-token=42d07c42-6d61-4cc6-b8d0-7c87671a0a97:EwoA59lk/W5FAQAA:NwWpbeuMSo/Od9HGJSCKsuHpkf+0/xWsgBypuKJhZoQK9tTDgjjGLf2+2kA9umoVOqufBOJPSaH0XSUTcvZMiGX4ygSJCi3IwJX4uL0M31ZzT8sG7VSSr6/LxgI9yQMJl1pnGyq1q3J7tchiq8oV9x0FEpidRrQkrCJngkWwycDB9FH4uzIu8vIEqAPIw6oY7hJyEhDVEmK94IR+u5Nk1UYM/Aa7NVCuT4LexSISfP3evRdss3JNSGj+8pikfuyWIKIA4mz6EIV3iYwoW9o="
            ),
            "priority": "u=1, i",
            "referer": "https://huggingface.co/spaces/HiDream-ai/HiDream-E1-Full",
            "sec-ch-ua": '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0"
            ),
        }

        # 使用 httpx 异步客户端（无代理）
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    try:
                        response_data = response.json()
                        print("响应内容:", json.dumps(response_data, indent=2, ensure_ascii=False))
                        self.token=response_data["token"]
                        self.accessToken=response_data["accessToken"]
                        self.exp=response_data["exp"]
                    except json.JSONDecodeError:
                        print("无法解析响应内容为 JSON:", response.text)
                else:
                    print(f"请求失败，状态码: {response.status_code}")
                    print("响应内容:", response.text)

            except httpx.RequestError as e:
                print(f"请求发生错误: {e}")
            except Exception as e:
                print(f"其他错误: {e}")



# 运行异步函数
if __name__ == "__main__":
    image_editor = ImageEditor()
    file_path = "D:\BlueArchive\Eridanus\img.png"  # 请替换为实际文件路径
    r=asyncio.run(image_editor.upload_file(file_path=file_path))
    print(r)
    r=asyncio.run(image_editor.fetch_jwt())
    print(r)