import httpx
import random
import zipfile
from bs4 import BeautifulSoup
import io
import base64
from plugins.utils.utils import random_str
from .setu_moderate import pic_audit_standalone


async def get_results(url,proxy=None):
    if proxy is not None:
        proxies = {"http://": proxy, "https://": proxy}
    else:
        proxies = None
    try:
        async with httpx.AsyncClient(proxies=proxies,timeout=100) as client:
            response = await client.get(url)
    except:
        return []
    if response:
        paths=[]
        d=response.json()["data"]
        for i in d:
            try:
                url=i["url"]
                async with httpx.AsyncClient(proxies=proxies,timeout=100) as client:
                    response = await client.get(url)
                p=f"data/pictures/cache/{random_str(10)}.png"
                with open(p,"wb") as f:
                    f.write(response.content)
                paths.append(p)
            except:
                continue
        return paths
    else:
        return []
async def ideo_gram(prompt,proxy=None):

    url=f"https://apiserver.alcex.cn/ideogram/generate-image?prompt={prompt}"
    return await get_results(url,proxy)

async def bing_dalle3(prompt,proxy=None):

    url=f"https://apiserver.alcex.cn/dall-e-3/generate-image?prompt={prompt}"
    return await get_results(url,proxy)
async def flux_speed(prompt,proxy=None):

    url=f"https://apiserver.alcex.cn/flux-speed/generate-image?prompt={prompt}"
    return await get_results(url,proxy)
async def recraft_v3(prompt,proxy=None):
    url=f"https://apiserver.alcex.cn/recraft-v3/generate-image?prompt={prompt}"
    return await get_results(url,proxy)
async def flux_ultra(prompt,proxy=None):
    url=f"https://apiserver.alcex.cn/flux-pro.ultra/generate-image?prompt={prompt}"
    return await get_results(url,proxy)
async def n4(prompt, path, groupid, config):
    url = "https://spawner.goutou.art"

    if "方" in prompt:
        prompt = prompt.replace("方", "")
        width = 1024
        height = 1024
    elif "横" in prompt:
        prompt = prompt.replace("横", "")
        width = 1216
        height = 832
    else:
        width = 832
        height = 1216
    
    payload = {
        "input": f"{prompt}, rating:general, best quality, very aesthetic, absurdres",
        "model": "nai-diffusion-4-curated-preview",
        "action": "generate",
        "parameters": {
            "params_version": 3,
            "width": width,
            "height": height,
            "scale": 6,
            "sampler": "k_dpmpp_2m",
            "steps": 23,
            "n_samples": 1,
            "ucPreset": 0,
            "qualityToggle": True,
            "dynamic_thresholding": False,
            "controlnet_strength": 1,
            "legacy": False,
            "add_original_image": True,
            "cfg_rescale": 0,
            "noise_schedule": "exponential",
            "legacy_v3_extend": False,
            "skip_cfg_above_sigma": None,
            "use_coords": False,
            "seed": random.randint(0, 2**32 - 1),
            "characterPrompts": [],
            "v4_prompt": {
                "caption": {
                    "base_caption": f"{prompt}, rating:general, best quality, very aesthetic, absurdres",
                    "char_captions": []
                },
                "use_coords": False,
                "use_order": True
            },
            "v4_negative_prompt": {
                "caption": {
                    "base_caption": "blurry, lowres, error, film grain, scan artifacts, worst quality, bad quality, jpeg artifacts, very displeasing, chromatic aberration, logo, dated, signature, multiple views, gigantic breasts",
                    "char_captions": []
                }
            },
            "negative_prompt": "blurry, lowres, error, film grain, scan artifacts, worst quality, bad quality, jpeg artifacts, very displeasing, chromatic aberration, logo, dated, signature, multiple views, gigantic breasts",
            "reference_image_multiple": [],
            "reference_information_extracted_multiple": [],
            "reference_strength_multiple": [],
            "deliberate_euler_ancestral_bug": False,
            "prefer_brownian": True
        }
    }

    headers = {
        "Authorization": f"Bearer {config.api['nai_key']}"
    }
    if config.api["proxy"]["http_proxy"] is not None:
        proxies = {"http://": config.api["proxy"]["http_proxy"], "https://": config.api["proxy"]["http_proxy"]}
    else:
        proxies = None
    async with httpx.AsyncClient(timeout=1000, proxies=proxies) as client:
        response = await client.post(url=f'{url}/ai/generate-image', json=payload, headers=headers)
        response.raise_for_status()
        zip_content = response.content
        zip_file = io.BytesIO(zip_content)
        with zipfile.ZipFile(zip_file, 'r') as zf:
            file_names = zf.namelist()
            if not file_names:
                raise ValueError("The zip archive is empty.")
            file_name = file_names[0]
            if not file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                raise ValueError("The zip archive does not contain an image file.")
            image_data = zf.read(file_name)
            if groupid in config.controller["ai绘画"]["no_nsfw_groups"]:
                check = await pic_audit_standalone(base64.b64encode(image_data).decode('utf-8'), return_none=True, url=config.api["sd审核和反推api"])
                if check:
                    return False
            with open(path, 'wb') as img_file:
                img_file.write(image_data)
    return path

async def n3(prompt, negative_prompt, path, groupid,config):
    url = "https://image.novelai.net"

    if "方" in prompt:
        prompt = prompt.replace("方", "")
        width = 1024
        height = 1024
    elif "横" in prompt:
        prompt = prompt.replace("横", "")
        width = 1216
        height = 832
    else:
        width = 832
        height = 1216
    
    payload = {
        "input": f"{prompt}, best quality, amazing quality, very aesthetic, absurdres",
        "model": "nai-diffusion-3",
        "action": "generate",
        "parameters": {
            "params_version": 3,
            "width": width,
            "height": height,
            "scale": 5,
            "sampler": "k_dpmpp_2m",
            "steps": 23,
            "n_samples": 1,
            "ucPreset": 0,
            "qualityToggle": True,
            "sm": False,
            "sm_dyn": False,
            "dynamic_thresholding": False,
            "controlnet_strength": 1,
            "legacy": False,
            "add_original_image": True,
            "cfg_rescale": 0,
            "noise_schedule": "exponential",
            "legacy_v3_extend": False,
            "skip_cfg_above_sigma": None,
            "seed": random.randint(0, 2**32 - 1),
            "characterPrompts": [],
            "negative_prompt": "nsfw, lowres, {bad}, error, fewer, extra, missing, worst quality, jpeg artifacts, bad quality, watermark, unfinished, displeasing, chromatic aberration, signature, extra digits, artistic error, username, scan, [abstract]",
            "reference_image_multiple": [],
            "reference_information_extracted_multiple": [],
            "reference_strength_multiple": []
        }
    }

    headers = {
        "Authorization": f"Bearer {config.api['nai_key']}"
    }
    if config.api["proxy"]["http_proxy"] is not None:
        proxies = {"http://": config.api["proxy"]["http_proxy"], "https://": config.api["proxy"]["http_proxy"]}
    else:
        proxies = None
    async with httpx.AsyncClient(timeout=1000, proxies=proxies) as client:
        response = await client.post(url=f'{url}/ai/generate-image', json=payload, headers=headers)
        response.raise_for_status()
        zip_content = response.content
        zip_file = io.BytesIO(zip_content)
        with zipfile.ZipFile(zip_file, 'r') as zf:
            file_names = zf.namelist()
            if not file_names:
                raise ValueError("The zip archive is empty.")
            file_name = file_names[0]
            if not file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                raise ValueError("The zip archive does not contain an image file.")
            image_data = zf.read(file_name)
            if groupid in config.controller["ai绘画"]["no_nsfw_groups"]:
                check = await pic_audit_standalone(base64.b64encode(image_data).decode('utf-8'), return_none=True, url=config.api["sd审核和反推api"])
                if check:
                    return False
            with open(path, 'wb') as img_file:
                img_file.write(image_data)
    return path
