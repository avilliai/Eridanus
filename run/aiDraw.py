import asyncio
import base64
from io import BytesIO
import ruamel.yaml

import httpx
from bs4 import BeautifulSoup

from developTools.event.events import GroupMessageEvent
from developTools.message.message_components import Image, Node, Text
from plugins.aiDraw.aiArtModerate import aiArtModerate
from plugins.aiDraw.setu_moderate import pic_audit_standalone
from plugins.basic_plugin.ai_text2img import bing_dalle3, flux_ultra
from plugins.core.aiReplyCore_without_funcCall import aiReplyCore_shadow
from plugins.core.userDB import get_user
from plugins.utils.random_str import random_str
from plugins.aiDraw.aiDraw import  n4, n3, SdDraw0, SdreDraw, getloras, getcheckpoints, ckpt2, n4re0, n3re0,\
    SdmaskDraw
from plugins.aiDraw.wildcard import get_available_wildcards, replace_wildcards
from plugins.utils.utils import download_img, url_to_base64, parse_arguments

turn = 0
UserGet = {}
tag_user = {}
sd_user_args = {}
sd_re_args = {}
UserGet1 = {}
n4re = {}
n3re = {}
mask = {}
UserGetm = {}
default_prompt = {}
yaml = ruamel.yaml.YAML()
yaml.preserve_quotes = True
with open('config/controller.yaml', 'r', encoding='utf-8') as f:
    controller = yaml.load(f)
aiDrawController = controller.get("ai绘画")
ckpt = aiDrawController.get("sd默认启动模型") if aiDrawController else None
no_nsfw_groups = [int(item) for item in aiDrawController.get("no_nsfw_groups", [])] if aiDrawController else []

async def call_text2img(bot, event, config, prompt):
    tag = prompt

    tasks = [
        asyncio.create_task(func)
        for func in [
            call_text2img1(bot, event, config, tag),
            call_text2img2(bot, event, config, tag),
            nai4(bot, event, config, tag),  # 两个nai功能建议二选一
            # nai3(bot, event, config, tag), 
        ]
    ]
    r=None
    for future in asyncio.as_completed(tasks):
        try:
            f1=await future
            if f1:
                r=f1
        except Exception as e:
            bot.logger.error(f"Task failed: {e}")
    return {"img":r}
async def call_text2img2(bot, event, config, tag):
    prompt = tag
    user_info = await get_user(event.user_id, event.sender.nickname)
    
    if user_info[6] >= config.controller["basic_plugin"]["bing_dalle3_operate_level"] and config.controller["basic_plugin"]["内置ai绘画开关"]:
        bot.logger.info(f"Received text2img prompt: {prompt}")
        proxy = config.api["proxy"]["http_proxy"]

        functions = [
            bing_dalle3(prompt, proxy),
            flux_ultra(prompt, proxy),
            # ideo_gram(prompt, proxy),
            # flux_speed(prompt, proxy), #也不要这个
            # recraft_v3(prompt, proxy), #不要这个
        ]
        
        tasks = [asyncio.create_task(func) for func in functions]
        
        for future in asyncio.as_completed(tasks):
            try:
                result = await future
                if result:
                    sendMes = []
                    for r in result:
                        sendMes.append(Node(content=[Image(file=r)]))
                    await bot.send(event, sendMes)
            except Exception as e:
                bot.logger.error(f"Task failed with prompt '{prompt}': {e}")
    else:
        pass
        #await bot.send(event, "你没有权限使用该功能。")

async def call_text2img1(bot,event,config,tag):
    if config.settings["ai绘画"]["sd画图"] and config.api["ai绘画"]["sdUrl"] !="" and config.api["ai绘画"]["sdUrl"]!='':
        global turn
        global sd_user_args
        tag, log = await replace_wildcards(tag)
        if log:
            await bot.send(event, log)
        path = f"data/pictures/cache/{random_str()}.png"
        bot.logger.info(f"调用sd api: path:{path}|prompt:{tag} 当前队列人数：{turn}")
        try:
            if turn!=0:
                await bot.send(event, f'请求已加入绘图队列，当前排队任务数量：{turn}，请耐心等待~', True)
            else:
                await bot.send(event, f"正在绘制，请耐心等待~", True)
            turn += 1
            args = sd_user_args.get(event.sender.user_id, {})
            if hasattr(event, "group_id"):
                id_=event.group_id
            else:
                id_=event.user_id
            p = await SdDraw0(tag, path, config, id_, args)
            if p == False:
                turn -= 1
                bot.logger.info("色图已屏蔽")
                await bot.send(event, "杂鱼，色图不给你喵~", True)
            else:
                turn -= 1
                await bot.send(event, [Image(file=p)], True)
            return p
    
        except Exception as e:
            bot.logger.error(e)
            turn -= 1
            bot.logger.error(f"sd api调用失败。{e}")
            await bot.send(event, f"sd api调用失败。{e}")

async def call_aiArtModerate(bot,event,config,img_url):
    try:
        r=await aiArtModerate(img_url,config.api["sightengine"]["api_user"],config.api["sightengine"]["api_secret"])
        if config.api["llm"]["aiReplyCore"]:
            return {"msg":f"图片为ai创作的可能性为{r}%"}
        else:
            await bot.send(event, f"图片为ai创作的可能性为{r}%", True)
    except Exception as e:
        bot.logger.error(e)
        await bot.send(event, f"aiArtModerate调用失败。{e}")

async def nai4(bot, event, config, tag):
    if config.settings["ai绘画"]["novel_ai画图"]:
        tag, log = await replace_wildcards(tag)
        if log:
            await bot.send(event, log, True)
        path = f"data/pictures/cache/{random_str()}.png"
        bot.logger.info(f"发起nai4绘画请求，path:{path}|prompt:{tag}")

        retries_left = 50
        while retries_left > 0:
            try:
                p = await n4(tag, path, event.group_id, config, sd_user_args.get(event.sender.user_id, {}))
                if p is False:
                    bot.logger.info("色图已屏蔽")
                    await bot.send(event, "杂鱼，色图不给你喵~", True)
                else:
                    await bot.send(event, [Text("nai4画图结果"), Image(file=p)], True)
                return
            except Exception as e:
                retries_left -= 1
                #bot.logger.error(f"nai4报错{e}，剩余尝试次数：{retries_left}")  #别让用户看到免得问。
                if retries_left == 0:
                    bot.logger.info(f"nai4调用失败。{e}")
    
async def nai3(bot, event, config, tag):
    if config.settings["ai绘画"]["novel_ai画图"]:
        tag, log = await replace_wildcards(tag)
        if log:
            await bot.send(event, log, True)
        path = f"data/pictures/cache/{random_str()}.png"
        bot.logger.info(f"发起nai3绘画请求，path:{path}|prompt:{tag}")

        retries_left = 50
        while retries_left > 0:
            try:
                p = await n3(tag, path, event.group_id, config, sd_user_args.get(event.sender.user_id, {}))
                if p is False:
                    bot.logger.info("色图已屏蔽")
                    await bot.send(event, "杂鱼，色图不给你喵~", True)
                    break  # 结束循环，因为没有需要重试的情况
                else:
                    await bot.send(event, [Text("nai3画图结果"), Image(file=p)], True)
                    break  # 成功获取结果后结束循环
            except Exception as e:
                retries_left -= 1
                #bot.logger.error(f"nai3报错{e}，剩余尝试次数：{retries_left}")
                if retries_left == 0:
                    bot.logger.error(f"nai3调用失败。{e}")  # 别让用户看到免得问。

def main(bot,config):
    ai_img_recognize = {}
    @bot.on(GroupMessageEvent)
    async def search_image(event):
        if str(event.raw_message) == "ai图检测" or (
                event.get("at") and event.get("at")[0]["qq"] == str(bot.id) and event.get("text")[0] == "ai图检测"):
            await bot.send(event, "请发送要检测的图片")
            ai_img_recognize[event.sender.user_id] = []
        if ("ai图检测" in str(event.raw_message) or event.sender.user_id in ai_img_recognize) and event.get('image'):
            img_url = event.get("image")[0]["url"]
            await call_aiArtModerate(bot, event, config, img_url)
            ai_img_recognize.pop(event.sender.user_id)

    @bot.on(GroupMessageEvent)
    async def bing_dalle3_draw(event):  #无需配置的ai绘图接口
        if str(event.raw_message).startswith("画 "):
            prompt = str(event.raw_message).split("画 ")[1]
            await call_text2img2(bot, event, config, prompt)
    
    @bot.on(GroupMessageEvent)
    async def naiDraw4(event):
        if str(event.raw_message).startswith("n4 ") and config.settings["ai绘画"]["novel_ai画图"]:
            tag = str(event.raw_message).replace("n4 ", "")
            await bot.send(event, '正在进行nai4画图', True)
            await nai4(bot,event,config,tag)

    @bot.on(GroupMessageEvent)
    async def naiDraw3(event):
        if str(event.raw_message).startswith("n3 ") and config.settings["ai绘画"]["novel_ai画图"]:
            tag = str(event.raw_message).replace("n3 ", "")
            await bot.send(event, '正在进行nai3画图', True)
            await nai3(bot,event,config,tag)

    @bot.on(GroupMessageEvent)
    async def db(event):
        if str(event.raw_message).startswith("dan "):
            tag = str(event.raw_message).replace("dan ", "")
            bot.logger.info(f"收到来自群{event.group_id}的请求，prompt:{tag}")
            await bot.send(event, f'正在搜索词条{tag}')
            limit = 5
            if config.api["proxy"]["http_proxy"] is not None:
                proxies = {"http://": config.api["proxy"]["http_proxy"], "https://": config.api["proxy"]["http_proxy"]}
            else:
                proxies = None

            db_base_url = "https://hijiribe.donmai.us"  # 这是反代，原来的是https://danbooru.donmai.us
            # 把danbooru换成sonohara、kagamihara、hijiribe这三个任意一个试试，后面的不用改

            build_msg = [Node(content=[Text(f"{tag}的搜索结果:")])]

            msg = tag
            try:
                async with httpx.AsyncClient(timeout=1000, proxies=proxies) as client:
                    resp = await client.get(
                        f"{db_base_url}/autocomplete?search%5Bquery%5D={msg}&search%5Btype%5D=tag_query&version=1&limit={limit}",
                        follow_redirects=True,
                    )
                    resp.raise_for_status()  # 检查请求是否成功
                    bot.logger.info(f"Autocomplete request successful for tag: {tag}")
            except Exception as e:
                bot.logger.error(f"Failed to get autocomplete data for tag: {tag}. Error: {e}")
                await bot.send(event,f"获取{tag}的搜索结果失败")
                return

            soup = BeautifulSoup(resp.text, 'html.parser')
            tags = soup.find_all('li', class_='ui-menu-item')

            data_values = []
            raw_data_values = []
            for tag in tags:
                data_value = tag['data-autocomplete-value']
                raw_data_values.append(data_value)
                data_value_space = data_value.replace('_', ' ')
                data_values.append(data_value_space)
                bot.logger.info(f"Found autocomplete tag: {data_value_space}")

            for tag in raw_data_values:
                tag1 = tag.replace('_', ' ')
                b1 = Node(content=[Text(f"{tag1}")])
                build_msg.append(b1)
                formatted_tag = tag.replace(' ', '_').replace('(', '%28').replace(')', '%29')

                try:
                    async with httpx.AsyncClient(timeout=1000, proxies=proxies) as client:
                        image_resp = await client.get(
                            f"{db_base_url}/posts?tags={formatted_tag}",
                            follow_redirects=True
                        )
                        image_resp.raise_for_status()  # 检查请求是否成功
                        bot.logger.info(f"Posts request successful for tag: {formatted_tag}")
                except Exception as e:
                    bot.logger.error(f"Failed to get posts for tag: {formatted_tag}. Error: {e}")
                    continue  # 继续处理下一个标签

                soup = BeautifulSoup(image_resp.text, 'html.parser')
                img_urls = [img['src'] for img in soup.find_all('img') if img['src'].startswith('http')][:2]
                bot.logger.info(f"Found {len(img_urls)} images for tag: {formatted_tag}")

                async def download_img1(image_url: str) -> (str, bytes):
                    try:
                        async with httpx.AsyncClient(timeout=1000, proxies=proxies) as client:
                            response = await client.get(image_url)
                            response.raise_for_status()
                            content_type = response.headers.get('content-type', '').lower()
                            if not content_type.startswith('image/'):
                                raise ValueError(f"URL {image_url} does not point to an image.")
                            bytes_image = response.content

                            buffered = BytesIO(bytes_image)
                            base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

                            bot.logger.info(f"Downloaded image from URL: {image_url}")
                            return base64_image, bytes_image

                    except httpx.RequestError as e:
                        bot.logger.error(f"Failed to download image from {image_url}: {e}")
                        raise
                    except Exception as e:
                        bot.logger.error(f"An error occurred while processing the image from {image_url}: {e}")
                        raise

                async def process_image(image_url):
                    try:
                        base64_image, bytes_image = await download_img1(image_url)
                        if event.group_id in no_nsfw_groups:
                            audit_result = await pic_audit_standalone(base64_image, return_none=True,
                                                                      url=config.api["ai绘画"]["sd审核和反推api"])
                            if audit_result:
                                bot.logger.info(f"Image at URL {image_url} was flagged by audit: {audit_result}")
                                return [Text(f"太涩了{image_url}")]
                        bot.logger.info(f"Image at URL {image_url} passed the audit")
                        path = f"data/pictures/cache/{random_str()}.png"
                        p = await download_img(image_url, path)
                        return [Image(file=p), Text(image_url)]
                    except Exception as e:
                        bot.logger.error(f"Failed to process image at {image_url}: {e}")
                        return None

                async def process_images(img_urls):
                    tasks = [process_image(url) for url in img_urls]
                    results = await asyncio.gather(*tasks, return_exceptions=True)

                    # 过滤掉异常和 None 结果
                    filtered_results = [result for result in results if
                                        not isinstance(result, Exception) and result is not None]

                    # 创建 ForwardMessageNode 列表
                    forward_messages = [
                        Node(
                            content=result
                        )
                        for result in filtered_results
                    ]

                    bot.logger.info(f"Processed {len(filtered_results)} images for tag: {formatted_tag}")
                    return forward_messages

                results = await process_images(img_urls)
                build_msg.extend(results)

            try:
                await bot.send(event, build_msg)
                bot.logger.info("Successfully sent the compiled message to the group.")
            except Exception as e:
                await bot.send(event, f"发送失败{e}")
                bot.logger.error(f"Failed to send the compiled message to the group. Error: {e}")

    @bot.on(GroupMessageEvent)
    async def tagger(event):
        global tag_user

        if event.get('image') == None and (
                str(event.raw_message) == ("tag") or str(event.raw_message).startswith("tag ")):
            tag_user[event.sender.user_id] = []
            await bot.send(event, "请发送要识别的图片")

        # 处理图片和重绘命令
        if (str(event.raw_message).startswith("tag") or event.sender.user_id in tag_user) and event.get('image'):
            if (str(event.raw_message).startswith("tag")) and event.get('image'):
                tag_user[event.sender.user_id] = []

            # 日志记录
            bot.logger.info(f"接收来自群：{event.group_id} 用户：{event.sender.user_id} 的tag反推指令")

            # 获取图片路径
            path = f"data/pictures/cache/{random_str()}.png"
            img_url = event.get("image")[0]["url"]
            bot.logger.info(f"发起反推tag请求，path:{path}")
            tag_user.pop(event.sender.user_id)

            try:
                b64_in = await url_to_base64(img_url)
                await bot.send(event, "tag反推中", True)
                message, tags, tags_str = await pic_audit_standalone(b64_in, is_return_tags=True,
                                                                     url=config.api["ai绘画"]["sd审核和反推api"])
                tags_str = tags_str.replace("_", " ")
                await bot.send(event, Text(tags_str), True)
            except Exception as e:
                bot.logger.error(f"反推失败: {e}")
                await bot.send(event, f"反推失败: {e}", True)

    @bot.on(GroupMessageEvent)
    async def sdsettings(event):
        if str(event.raw_message).startswith("setsd "):
            global sd_user_args
            sd_user_args.setdefault(event.sender.user_id, {})
            command = str(event.raw_message).replace("setsd ", "")
            if command == "0":
                sd_user_args[event.sender.user_id] = {}
                await bot.send(event, f"当前绘画参数已重置", True)
                return
            cmd_dict = parse_arguments(command, sd_user_args[event.sender.user_id])  # 不需要 await
            sd_user_args[event.sender.user_id] = cmd_dict
            await bot.send(event, f"当前绘画参数设置: {sd_user_args[event.sender.user_id]}", True)

    @bot.on(GroupMessageEvent)
    async def sdresettings(event):
        if str(event.raw_message).startswith("setre "):
            global sd_re_args
            sd_re_args.setdefault(event.sender.user_id, {})
            command = str(event.raw_message).replace("setre ", "")
            if command == "0":
                sd_re_args[event.sender.user_id] = {}
                await bot.send(event, f"当前重绘参数已重置", True)
                return
            cmd_dict = parse_arguments(command, sd_re_args[event.sender.user_id])  # 不需要 await
            sd_re_args[event.sender.user_id] = cmd_dict
            await bot.send(event, f"当前重绘参数设置: {sd_re_args[event.sender.user_id]}", True)

    @bot.on(GroupMessageEvent)
    async def sdreDrawRun(event):
        global UserGet
        global turn

        if event.get('image') == None and (
                str(event.raw_message) == ("重绘") or str(event.raw_message).startswith("重绘 ")):
            prompt = str(event.raw_message).replace("重绘", "").strip()
            UserGet[event.sender.user_id] = [prompt]
            await bot.send(event, "请发送要重绘的图片")

        # 处理图片和重绘命令
        if (str(event.raw_message).startswith("重绘") or event.sender.user_id in UserGet) and event.get('image'):
            if (str(event.raw_message).startswith("重绘")) and event.get('image'):
                prompt = str(event.raw_message).replace("重绘", "").strip()
                UserGet[event.sender.user_id] = [prompt]

            # 日志记录
            prompts = ', '.join(UserGet[event.sender.user_id])
            if prompts:
                prompts,log = await replace_wildcards(prompts)
                if log:
                    await bot.send(event, log, True)
            bot.logger.info(f"接收来自群：{event.group_id} 用户：{event.sender.user_id} 的重绘指令 prompt: {prompts}")

            # 获取图片路径
            path = f"data/pictures/cache/{random_str()}.png"
            img_url = event.get("image")[0]["url"]
            bot.logger.info(f"发起SDai重绘请求，path:{path}|prompt:{prompts}")
            prompts_str = ' '.join(UserGet[event.sender.user_id]) + ' '
            UserGet.pop(event.sender.user_id)

            try:
                args = sd_re_args.get(event.sender.user_id, {})
                b64_in = await url_to_base64(img_url)

                await bot.send(event, f"开始重绘啦~sd前面排队{turn}人，请耐心等待喵~", True)
                turn += 1
                # 将 UserGet[event.sender.user_id] 列表中的内容和 positive_prompt 合并成一个字符串
                p = await SdreDraw(prompts_str, path, config, event.group_id, b64_in, args)
                if p == False:
                    turn -= 1
                    bot.logger.info("色图已屏蔽")
                    await bot.send(event, "杂鱼，色图不给你喵~", True)
                else:
                    turn -= 1
                    await bot.send(event, [Text("sd重绘结果"),Image(file=p)], True)
            except Exception as e:
                bot.logger.error(f"重绘失败: {e}")
                await bot.send(event, f"sd api重绘失败。{e}", True)

    @bot.on(GroupMessageEvent)
    async def AiSdDraw(event):
        global turn
        global sd_user_args
        if str(event.raw_message).startswith("画 ") and config.settings["ai绘画"]["sd画图"] and config.api["ai绘画"]["sdUrl"] !="" and config.api["ai绘画"]["sdUrl"]!='':
            tag = str(event.raw_message).replace("画 ", "")
            await call_text2img1(bot,event,config,tag)
        if str(event.raw_message) == "lora" and config.settings["ai绘画"]["sd画图"]:  # 获取lora列表
            bot.logger.info('查询loras中...')
            try:
                p = await getloras(config)
                bot.logger.info(str(p))
                await bot.send(event, p, True)
                # logger.info("success")
            except Exception as e:
                bot.logger.error(e)

        if str(event.raw_message) == "ckpt" and config.settings["ai绘画"]["sd画图"]:  # 获取lora列表
            bot.logger.info('查询checkpoints中...')
            try:
                p = await getcheckpoints(config)
                bot.logger.info(str(p))
                await bot.send(event, p, True)
                # logger.info("success")
            except Exception as e:
                bot.logger.error(e)

        if str(event.raw_message).startswith("ckpt2 ") and config.settings["ai绘画"]["sd画图"]:
            tag = str(event.raw_message).replace("ckpt2 ", "")
            bot.logger.info('切换ckpt中')
            if event.user_id == config.basic_config["master"]["id"]:
                try:
                    await ckpt2(tag,config)
                    await bot.send(event, "切换成功喵~第一次会慢一点~", True)
                    # logger.info("success")
                except Exception as e:
                    bot.logger.error(e)
                    await bot.send(event, "ckpt切换失败", True)
            else:
                await bot.send(event, "仅master可执行此操作", True)

    @bot.on(GroupMessageEvent)
    async def wdcard(event):
        message = str(event.raw_message)
        if message == 'getwd':
            r = await get_available_wildcards()
            await bot.send(event, r, True)
        elif message.startswith('getwd '):
            prompts = message.replace("getwd ", "")
            if prompts:
                prompts, log = await replace_wildcards(prompts)
                if log:
                    await bot.send(event, prompts)
                

    @bot.on(GroupMessageEvent)
    async def n4reDrawRun(event):
        global n4re
        global turn

        if event.get('image') == None and (
                str(event.raw_message) == ("n4re") or str(event.raw_message).startswith("n4re ")):
            prompt = str(event.raw_message).replace("n4re", "").strip()
            n4re[event.sender.user_id] = [prompt]
            await bot.send(event, "请发送要重绘的图片")

        # 处理图片和重绘命令
        if (str(event.raw_message).startswith("n4re") or event.sender.user_id in n4re) and event.get('image'):
            if (str(event.raw_message).startswith("n4re")) and event.get('image'):
                prompt = str(event.raw_message).replace("n4re", "").strip()
                n4re[event.sender.user_id] = [prompt]

            # 日志记录
            prompts = ', '.join(n4re[event.sender.user_id])
            if prompts:
                prompts,log = await replace_wildcards(prompts)
                if log:
                    await bot.send(event, log, True)
            bot.logger.info(f"接收来自群：{event.group_id} 用户：{event.sender.user_id} 的n4re指令 prompt: {prompts}")

            # 获取图片路径
            path = f"data/pictures/cache/{random_str()}.png"
            img_url = event.get("image")[0]["url"]
            bot.logger.info(f"发起n4re请求，path:{path}|prompt:{prompts}")
            prompts_str = ' '.join(n4re[event.sender.user_id]) + ' '
            await bot.send(event, "正在nai4重绘",True)
            n4re.pop(event.sender.user_id)

            async def attempt_draw(retries_left=50):  # 这里是递归请求的次数
                try:
                    args = sd_re_args.get(event.sender.user_id, {})
                    b64_in = await url_to_base64(img_url)
                    # 将 n4re[event.sender.user_id] 列表中的内容和 positive_prompt 合并成一个字符串
                    p = await n4re0(prompts_str, path, event.group_id, config, b64_in, args)
                    if p == False:
                        bot.logger.info("色图已屏蔽")
                        await bot.send(event, "杂鱼，色图不给你喵~", True)
                    else:
                        await bot.send(event, [Text("nai4重绘结果"),Image(file=p)], True)
                except Exception as e:
                    bot.logger.error(e)
                    if retries_left > 0:
                        bot.logger.error(f"尝试重新请求nai4re，剩余尝试次数：{retries_left - 1}")
                        await attempt_draw(retries_left - 1)
                    else:
                        await bot.send(event, f"nai4重绘失败。{e}", True)

            await attempt_draw()

    @bot.on(GroupMessageEvent)
    async def n3reDrawRun(event):
        global n3re
        global turn

        if event.get('image') == None and (
                str(event.raw_message) == ("n3re") or str(event.raw_message).startswith("n3re ")):
            prompt = str(event.raw_message).replace("n3re", "").strip()
            n3re[event.sender.user_id] = [prompt]
            await bot.send(event, "请发送要重绘的图片")

        # 处理图片和重绘命令
        if (str(event.raw_message).startswith("n3re") or event.sender.user_id in n3re) and event.get('image'):
            if (str(event.raw_message).startswith("n3re")) and event.get('image'):
                prompt = str(event.raw_message).replace("n3re", "").strip()
                n3re[event.sender.user_id] = [prompt]

            # 日志记录
            prompts = ', '.join(n3re[event.sender.user_id])
            if prompts:
                prompts,log = await replace_wildcards(prompts)
                if log:
                    await bot.send(event, log, True)
            bot.logger.info(f"接收来自群：{event.group_id} 用户：{event.sender.user_id} 的n3re指令 prompt: {prompts}")

            # 获取图片路径
            path = f"data/pictures/cache/{random_str()}.png"
            img_url = event.get("image")[0]["url"]
            bot.logger.info(f"发起n3re请求，path:{path}|prompt:{prompts}")
            prompts_str = ' '.join(n3re[event.sender.user_id]) + ' '
            await bot.send(event, "正在nai3重绘",True)
            n3re.pop(event.sender.user_id)

            async def attempt_draw(retries_left=50):  # 这里是递归请求的次数
                try:
                    args = sd_re_args.get(event.sender.user_id, {})
                    b64_in = await url_to_base64(img_url)
                    # 将 n3re[event.sender.user_id] 列表中的内容和 positive_prompt 合并成一个字符串
                    p = await n3re0(prompts_str, path, event.group_id, config, b64_in, args)
                    if p == False:
                        bot.logger.info("色图已屏蔽")
                        await bot.send(event, "杂鱼，色图不给你喵~", True)
                    else:
                        await bot.send(event, [Text("nai3重绘结果"),Image(file=p)], True)
                except Exception as e:
                    bot.logger.error(e)
                    if retries_left > 0:
                        bot.logger.error(f"尝试重新请求nai3re，剩余尝试次数：{retries_left - 1}")
                        await attempt_draw(retries_left - 1)
                    else:
                        await bot.send(event, f"nai3重绘失败。{e}", True)

            await attempt_draw()

    @bot.on(GroupMessageEvent)
    async def sdmaskDrawRun(event):
        global UserGetm
        global turn
        global mask

        if event.get('image') == None and (
                str(event.raw_message) == ("局部重绘") or str(event.raw_message).startswith("局部重绘 ")):
            prompt = str(event.raw_message).replace("局部重绘 ", "").strip()
            UserGetm[event.sender.user_id] = prompt  # 直接将值设置为字符串
            await bot.send(event, "请发送要局部重绘的图片")

        # 处理图片和重绘命令
        
        if event.sender.user_id in UserGetm and event.get('image') and event.sender.user_id in mask:
            path = f"data/pictures/cache/{random_str()}.png"
            prompts = UserGetm[event.sender.user_id]  # 直接使用字符串
            mask_url = event.get("image")[0]["url"]
            img_url = mask[event.sender.user_id]  # 直接使用字符串
            bot.logger.info(f"接收来自群：{event.group_id} 用户：{event.sender.user_id} 的局部重绘指令 prompt: {prompts}")
            UserGetm.pop(event.sender.user_id)
            mask.pop(event.sender.user_id)

            try:
                args = sd_re_args.get(event.sender.user_id, {})
                b64_in = await url_to_base64(img_url)
                mask_b64 = await url_to_base64(mask_url)

                await bot.send(event, f"开始局部重绘啦~sd前面排队{turn}人，请耐心等待喵~", True)
                turn += 1
                p = await SdmaskDraw(prompts, path, config, event.group_id, b64_in, args, mask_b64)
                if p == False:
                    turn -= 1
                    bot.logger.info("色图已屏蔽")
                    await bot.send(event, "杂鱼，色图不给你喵~", True)
                else:
                    turn -= 1
                    await bot.send(event, [Text("sd局部重绘结果"),Image(file=p)], True)
            except Exception as e:
                bot.logger.error(f"局部重绘失败: {e}")
                await bot.send(event, f"sd api局部重绘失败。{e}", True)
            return

        if (str(event.raw_message).startswith("局部重绘") or event.sender.user_id in UserGetm) and event.get('image'):
            if (str(event.raw_message).startswith("局部重绘 ")) and event.get('image'):
                prompts = str(event.raw_message).replace("局部重绘 ", "").strip()
                UserGetm[event.sender.user_id] = prompts

            prompts = UserGetm[event.sender.user_id]
            # 日志记录
            if prompts:
                prompts, log = await replace_wildcards(prompts)
                if log:
                    await bot.send(event, log, True)
                UserGetm[event.sender.user_id] = prompts  # 直接将值设置为字符串

            img_url = event.get("image")[0]["url"]
            await bot.send(event, "请发送蒙版")
            mask[event.sender.user_id] = img_url  # 直接将值设置为字符串
            return


        if (str(event.raw_message).startswith("局部重绘") or event.sender.user_id in UserGetm) and event.get('image'):
            if (str(event.raw_message).startswith("局部重绘")) and event.get('image'):
                prompt = str(event.raw_message).replace("局部重绘", "").strip()

            # 日志记录
            prompts = ', '.join(UserGetm[event.sender.user_id])
            prompts,log = await replace_wildcards(prompts)
            if log:
                await bot.send(event, log, True)
            UserGetm[event.sender.user_id] = [prompt]

            img_url = event.get("image")[0]["url"]
            await bot.send(event, "请发送蒙版")
            mask[event.sender.user_id] = [img_url]
            return
                
    @bot.on(GroupMessageEvent)
    async def end_re(event):
        if str(event.raw_message) == ("/clearre"):
            global UserGet
            global tag_user
            global UserGet1
            global n4re
            global n3re
            global mask
            global UserGetm
            
            dictionaries = {
                'UserGet': UserGet,
                'tag_user': tag_user,
                'UserGet1': UserGet1,
                'n4re': n4re,
                'n3re': n3re,
                'mask': mask,
                'UserGetm': UserGetm
            }

            user_id = event.sender.user_id

            for dict_name, dictionary in dictionaries.items():
                # 确保dictionary是一个字典
                if isinstance(dictionary, dict):
                    try:
                        dictionary.pop(user_id)
                        bot.logger.info(f"User ID {user_id} cleared in {dict_name}.")
                    except KeyError:
                        bot.logger.info(f"User ID {user_id} not found in {dict_name}.")
                else:
                    bot.logger.info(f"Expected a dictionary for {dict_name}, but got {type(dictionary)}.")
            
            await bot.send(event, "已清除所有输入图片和文本缓存", True)
            
