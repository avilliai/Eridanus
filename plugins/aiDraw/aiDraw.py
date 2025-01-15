import httpx

import random
import zipfile
from bs4 import BeautifulSoup
import io
import base64

from .setu_moderate import pic_audit_standalone
import ruamel.yaml
import json
from PIL import Image

yaml = ruamel.yaml.YAML()
yaml.preserve_quotes = True
with open('config/controller.yaml', 'r', encoding='utf-8') as f:
    controller = yaml.load(f)
aiDrawController = controller.get("ai绘画")
ckpt = aiDrawController.get("sd默认启动模型") if aiDrawController else None
no_nsfw_groups = [int(item) for item in aiDrawController.get("no_nsfw_groups", [])] if aiDrawController else []
censored_words = ["nsfw", "nipples", "pussy", "areola", "dick", "cameltoe", "ass", "boob", "arse", "penis", "porn", "sex", "bitch", "fuck", "arse", "blowjob", "handjob", "anal", "nude", "vagina", "boner"]


from plugins.utils.random_str import random_str
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

    if groupid in no_nsfw_groups:
        for word in censored_words:
            if word in prompt:
                return False

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
            "seed": random.randint(0, 2 ** 32 - 1),
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
        "Authorization": f"Bearer {config.api['ai绘画']['nai_key']}"
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
            if groupid in no_nsfw_groups:
                check = await pic_audit_standalone(base64.b64encode(image_data).decode('utf-8'), return_none=True,
                                                   url=config.api["ai绘画"]["sd审核和反推api"])
                if check:
                    return False
            with open(path, 'wb') as img_file:
                img_file.write(image_data)
    return path


async def n3(prompt, path, groupid, config):
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

    if groupid in no_nsfw_groups:
        for word in censored_words:
            if word in prompt:
                return False

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
            "seed": random.randint(0, 2 ** 32 - 1),
            "characterPrompts": [],
            "negative_prompt": "nsfw, lowres, {bad}, error, fewer, extra, missing, worst quality, jpeg artifacts, bad quality, watermark, unfinished, displeasing, chromatic aberration, signature, extra digits, artistic error, username, scan, [abstract]",
            "reference_image_multiple": [],
            "reference_information_extracted_multiple": [],
            "reference_strength_multiple": []
        }
    }

    headers = {
        "Authorization": f"Bearer {config.api['ai绘画']['nai_key']}"
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
            if groupid in no_nsfw_groups:
                check = await pic_audit_standalone(base64.b64encode(image_data).decode('utf-8'), return_none=True,
                                                   url=config.api["ai绘画"]["sd审核和反推api"])
                if check:
                    return False
            with open(path, 'wb') as img_file:
                img_file.write(image_data)
    return path


async def SdreDraw(prompt, path, config, groupid, b64_in, args):
    url = config.api["ai绘画"]["sdUrl"]
    args = args
    width = (args.get('w', 1024) if args.get('w', 1024) > 0 else 1024) if isinstance(args, dict) else 1024
    height = (args.get('h', 1024) if args.get('h', 1024) > 0 else 1024) if isinstance(args, dict) else 1024
    denoising_strength = (args.get('d', 0.7) if args.get('d', 0.7) > 0 else 0.7) if isinstance(args, dict) else 0.7
    
    if width > 1600:
        width = 1600
    if height > 1600:
        height = 1600

    if groupid in no_nsfw_groups:
        for word in censored_words:
            if word in prompt:
                return False
    
    payload = {
        "init_images": [b64_in],
        "denoising_strength": denoising_strength,
        "enable_hr": 'true',
        "hr_scale": 1.5,
        "hr_second_pass_steps": 15,
        "hr_upscaler": 'SwinIR_4x',
        "prompt": f'score_9,score_8_up,score_7_up,{prompt},masterpiece,best quality,amazing quality,very aesthetic,absurdres,newest,',
        "negative_prompt": '((nsfw)),score_6,score_5,score_4,((furry)),lowres,(bad quality,worst quality:1.2),bad anatomy,sketch,jpeg artifacts,ugly, poorly drawn,(censor),blurry,watermark,simple background,transparent background',
        "seed": -1,
        "batch_size": 1,
        "n_iter": 1,
        "steps": 35,
        "cfg_scale": 6.5,
        "width": width,
        "height": height,
        "restore_faces": False,
        "tiling": False,
        "sampler_name": 'Euler a',
        "scheduler": 'Align Your Steps',
        "clip_skip_steps": 2,
        "override_settings": {
            "CLIP_stop_at_last_layers": 2,
            "sd_model_checkpoint": ckpt,  # 指定大模型
        },
        "override_settings_restore_afterwards": False,
    }  # manba out
    headers = {
        "Authorization": f"Bearer {config.api['ai绘画']['nai_key']}"
    }
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(url=f'{url}/sdapi/v1/img2img', json=payload)
    r = response.json()
    if 'images' not in r or len(r['images']) == 0:
        return None
    # 我的建议是，直接返回base64，让它去审查
    b64 = r['images'][0]
    if groupid in no_nsfw_groups:  # 推荐用kaggle部署sd，防止占线（kaggle搜spawnerqwq）
        check = await pic_audit_standalone(b64, return_none=True, url=config.api["ai绘画"][
            "sd审核和反推api"])  # 这里如果是使用我（spawnerqwq）的kaggle云端脚本部署的sd，参数可以写(b64,return_none=True,url)
        if check:  # 注意自己装的wd14打标插件没用，官方插件有bug，我在kaggle部署的插件是修改过的
            return False  # 注意这里的url是sdurl，如果你在不是sd的画图模块也想开审核，注意把那个url的参数填sdurl
    image = Image.open(io.BytesIO(base64.b64decode(r['images'][0])))
    # image = Image.open(io.BytesIO(base64.b64decode(p)))
    image.save(f'{path}')
    # image.save(f'{path}')
    return path


async def SdDraw0(prompt, path, config, groupid, args):
    url = config.api["ai绘画"]["sdUrl"]

    args = args
    width = (args.get('w', 1064) if args.get('w', 1064) > 0 else 1064) if isinstance(args, dict) else 1064
    height = (args.get('h', 1600) if args.get('h', 1600) > 0 else 1600) if isinstance(args, dict) else 1600
    denoising_strength = (args.get('d', 0.7) if args.get('d', 0.7) > 0 else 0.7) if isinstance(args, dict) else 0.7
    
    if width > 1600:
        width = 1600
    if height > 1600:
        height = 1600

    if groupid in no_nsfw_groups:
        for word in censored_words:
            if word in prompt:
                return False
    
    payload = {
        "denoising_strength": denoising_strength,
        "enable_hr": 'false',
        "hr_scale": 1.5,
        "hr_second_pass_steps": 15,
        "hr_upscaler": 'SwinIR_4x',
        "prompt": f'score_9,score_8_up,score_7_up,{prompt},masterpiece,best quality,amazing quality,very aesthetic,absurdres,newest,',
        "negative_prompt": '((nsfw)),score_6,score_5,score_4,((furry)),lowres,(bad quality,worst quality:1.2),bad anatomy,sketch,jpeg artifacts,ugly, poorly drawn,(censor),blurry,watermark,simple background,transparent background',
        "seed": -1,
        "batch_size": 1,
        "n_iter": 1,
        "steps": 35,
        "cfg_scale": 6.5,
        "width": width,
        "height": height,
        "restore_faces": False,
        "tiling": False,
        "sampler_name": 'Euler a',
        "scheduler": 'Align Your Steps',
        "clip_skip_steps": 2,
        "override_settings": {
            "CLIP_stop_at_last_layers": 2,
            "sd_model_checkpoint": ckpt,  # 指定大模型
        },
        "override_settings_restore_afterwards": False,
    }  # manba out
    headers = {
        "Authorization": f"Bearer {config.api['ai绘画']['nai_key']}"
    }
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
    r = response.json()

    b64 = r['images'][0]
    if groupid in no_nsfw_groups:  # 推荐用kaggle部署sd，防止占线（kaggle搜spawnerqwq）
        check = await pic_audit_standalone(b64, return_none=True, url=config.api["ai绘画"][
            "sd审核和反推api"])  # 这里如果是使用我（spawnerqwq）的kaggle云端脚本部署的sd，参数可以写(b64,return_none=True,url)
        if check:  # 注意自己装的wd14打标插件没用，官方插件有bug，我在kaggle部署的插件是修改过的
            return False  # 注意这里的url是sdurl，如果你在不是sd的画图模块也想开审核，注意把那个url的参数填sdurl
    image = Image.open(io.BytesIO(base64.b64decode(r['images'][0])))
    # image = Image.open(io.BytesIO(base64.b64decode(p)))
    image.save(f'{path}')
    # image.save(f'{path}')
    return path


async def getloras(config):
    url = f'{config.api["ai绘画"]["sdUrl"]}/sdapi/v1/loras'
    headers = {
        "Authorization": f"Bearer {config.api['ai绘画']['nai_key']}"
    }
    if config.api["proxy"]["http_proxy"] is not None:
        proxies = {"http://": config.api["proxy"]["http_proxy"], "https://": config.api["proxy"]["http_proxy"]}
    else:
        proxies = None
    async with httpx.AsyncClient(timeout=None, proxies=proxies) as client:
        response = await client.get(url)
        r = response.json()
        result_lines = [f'<lora:{lora.get("name", "未知")}:1.0>,' for lora in r]
        result = '以下是可用的lora：\n' + '\n'.join(result_lines) + '\n'
        return result


async def ckpt2(model, config):
    global ckpt
    ckpt = model
    config.controller["ai绘画"]["sd默认启动模型"]=model
    config.save_yaml("controller")


async def getcheckpoints(config):
    url = f'{config.api["ai绘画"]["sdUrl"]}/sdapi/v1/sd-models'
    headers = {
        "Authorization": f"Bearer {config.api['ai绘画']['nai_key']}"
    }
    if config.api["proxy"]["http_proxy"] is not None:
        proxies = {"http://": config.api["proxy"]["http_proxy"], "https://": config.api["proxy"]["http_proxy"]}
    else:
        proxies = None
    async with httpx.AsyncClient(timeout=None, proxies=proxies) as client:
        response = await client.get(url)
        r = response.json()
        model_lines = [f'{model.get("model_name", "未知")}.safetensors' for model in r]
        result = f'当前底模: {ckpt}\n以下是可用的底模：\n' + '\n'.join(model_lines) + '\n'
        return result

async def n4re0(prompt, path, groupid, config, b64_in, args):
    args = args
    url = "https://image.novelai.net"
    denoising_strength = (args.get('d', 0.7) if args.get('d', 0.7) > 0 else 0.7) if isinstance(args, dict) else 0.7

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

    if groupid in no_nsfw_groups:
        for word in censored_words:
            if word in prompt:
                return False

    payload = {
        "input": f"{prompt}, rating:general, best quality, very aesthetic, absurdres",
        "model": "nai-diffusion-4-curated-preview",
        "action": "img2img",
        "parameters": {
            "params_version": 3,
            "width": width,
            "height": height,
            "scale": 6,
            "sampler": "k_dpmpp_2m",
            "steps": 23,
            "n_samples": 1,
            "strength": denoising_strength,
            "noise": 0.2,
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
            "seed": random.randint(0, 2 ** 32 - 1),
            "image": b64_in,
            "characterPrompts": [],
            "extra_noise_seed": random.randint(0, 2 ** 32 - 1),
            "v4_prompt": {
                "caption": {
                    "base_caption": ", rating:general, best quality, very aesthetic, absurdres",
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
        "Authorization": f"Bearer {config.api['ai绘画']['nai_key']}"
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
            if groupid in no_nsfw_groups:
                check = await pic_audit_standalone(base64.b64encode(image_data).decode('utf-8'), return_none=True,
                                                   url=config.api["ai绘画"]["sd审核和反推api"])
                if check:
                    return False
            with open(path, 'wb') as img_file:
                img_file.write(image_data)
    return path

async def n3re0(prompt, path, groupid, config, b64_in, args):
    args = args
    url = "https://image.novelai.net"
    denoising_strength = (args.get('d', 0.7) if args.get('d', 0.7) > 0 else 0.7) if isinstance(args, dict) else 0.7

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

    if groupid in no_nsfw_groups:
        for word in censored_words:
            if word in prompt:
                return False

    payload = {
        "input": f"{prompt}, rating:general, best quality, very aesthetic, absurdres",
        "model": "nai-diffusion-3",
        "action": "img2img",
        "parameters": {
            "params_version": 3,
            "width": width,
            "height": height,
            "scale": 6,
            "sampler": "k_dpmpp_2m",
            "steps": 23,
            "n_samples": 1,
            "strength":denoising_strength,
            "noise":0.2,
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
            "seed": random.randint(0, 2 ** 32 - 1),
            "image": b64_in,
            "characterPrompts": [],
            "extra_noise_seed": random.randint(0, 2 ** 32 - 1),
            "negative_prompt": "blurry, lowres, error, film grain, scan artifacts, worst quality, bad quality, jpeg artifacts, very displeasing, chromatic aberration, logo, dated, signature, multiple views, gigantic breasts",
            "reference_image_multiple": [],
            "reference_information_extracted_multiple": [],
            "reference_strength_multiple": [],
            "deliberate_euler_ancestral_bug": False,
            "prefer_brownian": True
        }
    }

    headers = {
        "Authorization": f"Bearer {config.api['ai绘画']['nai_key']}"
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
            if groupid in no_nsfw_groups:
                check = await pic_audit_standalone(base64.b64encode(image_data).decode('utf-8'), return_none=True,
                                                   url=config.api["ai绘画"]["sd审核和反推api"])
                if check:
                    return False
            with open(path, 'wb') as img_file:
                img_file.write(image_data)
    return path

async def SdmaskDraw(prompt, path, config, groupid, b64_in, args, mask_base64):
    url = config.api["ai绘画"]["sdUrl"]
    args = args
    width = (args.get('w', 1024) if args.get('w', 1024) > 0 else 1024) if isinstance(args, dict) else 1024
    height = (args.get('h', 1024) if args.get('h', 1024) > 0 else 1024) if isinstance(args, dict) else 1024
    denoising_strength = (args.get('d', 0.7) if args.get('d', 0.7) > 0 else 0.7) if isinstance(args, dict) else 0.7
    
    if width > 1600:
        width = 1600
    if height > 1600:
        height = 1600

    if groupid in no_nsfw_groups:
        for word in censored_words:
            if word in prompt:
                return False

    payload = {
        "init_images": [b64_in],
        "mask": mask_base64,
        "mask_blur": 4,  # 边缘模糊
        "inpaint_full_res": False,  # 更高分辨率修复 耗费算力，一般显卡建议关闭
        "inpaint_full_res_padding": 4,  # 小到中等大小的修复区域 建议 4 - 10 大型修复区域建议 10 - 20
        "inpainting_mask_invert": 1,  # 0 则反转蒙版
        "denoising_strength": denoising_strength,
        "enable_hr": 'true',
        "hr_scale": 1.5,
        "hr_second_pass_steps": 15,
        "hr_upscaler": 'SwinIR_4x',
        "prompt": f'score_9,score_8_up,score_7_up,{prompt},masterpiece,best quality,amazing quality,very aesthetic,absurdres,newest,',
        "negative_prompt": '((nsfw)),score_6,score_5,score_4,((furry)),lowres,(bad quality,worst quality:1.2),bad anatomy,sketch,jpeg artifacts,ugly, poorly drawn,(censor),blurry,watermark,simple background,transparent background',
        "seed": -1,
        "batch_size": 1,
        "n_iter": 1,
        "steps": 35,
        "cfg_scale": 6.5,
        "width": width,
        "height": height,
        "restore_faces": False,
        "tiling": False,
        "sampler_name": 'Euler a',
        "scheduler": 'Align Your Steps',
        "clip_skip_steps": 2,
        "override_settings": {
            "CLIP_stop_at_last_layers": 2,
            "sd_model_checkpoint": ckpt,  # 指定大模型
        },
        "override_settings_restore_afterwards": False,
    }  # manba out
    headers = {
        "Authorization": f"Bearer {config.api['ai绘画']['nai_key']}"
    }
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(url=f'{url}/sdapi/v1/img2img', json=payload)
    r = response.json()
    if 'images' not in r or len(r['images']) == 0:
        return None
    # 我的建议是，直接返回base64，让它去审查
    b64 = r['images'][0]
    if groupid in no_nsfw_groups:  # 推荐用kaggle部署sd，防止占线（kaggle搜spawnerqwq）
        check = await pic_audit_standalone(b64, return_none=True, url=config.api["ai绘画"][
            "sd审核和反推api"])  # 这里如果是使用我（spawnerqwq）的kaggle云端脚本部署的sd，参数可以写(b64,return_none=True,url)
        if check:  # 注意自己装的wd14打标插件没用，官方插件有bug，我在kaggle部署的插件是修改过的
            return False  # 注意这里的url是sdurl，如果你在不是sd的画图模块也想开审核，注意把那个url的参数填sdurl
    image = Image.open(io.BytesIO(base64.b64decode(r['images'][0])))
    # image = Image.open(io.BytesIO(base64.b64decode(p)))
    image.save(f'{path}')
    # image.save(f'{path}')
    return path
