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
from plugins.utils.utils import parse_arguments
from plugins.utils.random_str import random_str

yaml = ruamel.yaml.YAML()
yaml.preserve_quotes = True
with open('config/settings.yaml', 'r', encoding='utf-8') as f:
    controller = yaml.load(f)
aiDrawController = controller.get("ai绘画")
ckpt = aiDrawController.get("sd默认启动模型") if aiDrawController else None
if_save = aiDrawController.get("sd图片是否保存到生图端") if aiDrawController else False
sd_w = int(aiDrawController.get("sd画图默认分辨率", "1024,1536").split(",")[0]) if aiDrawController else 1024
sd_h = int(aiDrawController.get("sd画图默认分辨率", "1024,1536").split(",")[1]) if aiDrawController else 1536
sdre_w = int(aiDrawController.get("sd重绘默认分辨率", "1064,1064").split(",")[0]) if aiDrawController else 1064
sdre_h = int(aiDrawController.get("sd重绘默认分辨率", "1064,1064").split(",")[1]) if aiDrawController else 1064
no_nsfw_groups = [int(item) for item in aiDrawController.get("no_nsfw_groups", [])] if aiDrawController else []
censored_words = ["nsfw", "nipple", "pussy", "areola", "dick", "cameltoe", "ass", "boob", "arse", "penis", "porn", "sex", "bitch", "fuck", "arse", "blowjob", "handjob", "anal", "nude", "vagina", "boner"]
positives = '{},rating:general, best quality, very aesthetic, absurdres'
negatives = 'blurry, lowres, error, film grain, scan artifacts, worst quality, bad quality, jpeg artifacts, very displeasing, chromatic aberration, logo, dated, signature, multiple views, gigantic breasts'
#positives = '{},masterpiece,best quality,amazing quality,very aesthetic,absurdres,newest,'
#negatives = 'nsfw,lowres,{bad},error,fewer,extra,missing,worst quality,jpeg artifacts,bad quality,watermark,unfinished,displeasing,chromatic aberration,signature,extra digits,artistic error,username,[abstract],blurry,film grain,scan artifacts,very displeasing,logo,dated,multiple views,gigantic breasts'
#negatives = '((nsfw)),((furry)),lowres,(bad quality,worst quality:1.2),bad anatomy,sketch,jpeg artifacts,ugly,poorly drawn,(censor),blurry,watermark,simple background,transparent background,{bad},error,fewer,extra,missing,jpeg artifacts,unfinished,displeasing,chromatic aberration,signature,extra digits,artistic error,username,scan,[abstract],film grain,scan artifacts,very displeasing,logo,dated,multiple views,gigantic breasts'
round_sd = 0
round_nai = 0

configs = aiDrawController.get("其他默认绘图参数",[])
default_args = {}

for config in configs:
    default_args = parse_arguments(config, default_args)

def check_censored(positive, censored_words):
    words = positive.lower().replace(',', ' ').split()
    for word in censored_words:
        if word.lower() in words:
            return True
    return

async def n4(prompt, path, groupid, config, args):
    global round_nai
    width = 832
    height = 1216
    url = "https://image.novelai.net"

    if "方" in prompt:
        prompt = prompt.replace("方", "")
        width = 1024
        height = 1024
    if "横" in prompt:
        prompt = prompt.replace("横", "")
        width = 1216
        height = 832
    if "竖" in prompt:
        prompt = prompt.replace("竖", "")
        width = 832
        height = 1216

    positive = str(args.get('p', default_args.get('p', positives)) if isinstance(args, dict) and isinstance(default_args, dict) else args.get('p', positives) if isinstance(args, dict) else default_args.get('p', positives) if isinstance(default_args, dict) else positives)
    negative = str(args.get('n', default_args.get('n', negatives)) if isinstance(args, dict) and isinstance(default_args, dict) else args.get('n', negatives) if isinstance(args, dict) else default_args.get('n', negatives) if isinstance(default_args, dict) else negatives)
    positive = (("{}," + positive) if "{}" not in positive else positive).replace("{}", prompt) if isinstance(positive, str) else str(prompt)
    nai_sampler = str(args.get('nai-sampler', default_args.get('nai-sampler', 'k_euler_ancestral')) if isinstance(args, dict) else default_args.get('nai-sampler', 'k_euler_ancestral') if isinstance(default_args, dict) else 'k_euler_ancestral')
    nai_scheduler = str(args.get('nai-scheduler', default_args.get('nai-scheduler', 'karras')) if isinstance(args, dict) else default_args.get('nai-scheduler', 'karras') if isinstance(default_args, dict) else 'karras')
    nai_cfg = float(args.get('nai-cfg', default_args.get('nai-cfg', 5)) if isinstance(args, dict) else default_args.get('nai-cfg', 5) if isinstance(default_args, dict) else 5)
    
    if groupid in no_nsfw_groups:
        if check_censored(positive, censored_words):
            return False

    payload = {
        "input": positive,
        "model": "nai-diffusion-4-curated-preview",
        "action": "generate",
        "parameters": {
            "params_version": 3,
            "width": width,
            "height": height,
            "scale": nai_cfg,
            "sampler": nai_sampler,
            "steps": 23,
            "n_samples": 1,
            "ucPreset": 0,
            "qualityToggle": True,
            "dynamic_thresholding": False,
            "controlnet_strength": 1,
            "legacy": False,
            "add_original_image": True,
            "cfg_rescale": 0,
            "noise_schedule": nai_scheduler,
            "legacy_v3_extend": False,
            "skip_cfg_above_sigma": None,
            "use_coords": False,
            "seed": random.randint(0, 2 ** 32 - 1),
            "characterPrompts": [],
            "v4_prompt": {
                "caption": {
                    "base_caption": positive,
                    "char_captions": []
                },
                "use_coords": False,
                "use_order": True
            },
            "v4_negative_prompt": {
                "caption": {
                    "base_caption": negative,
                    "char_captions": []
                }
            },
            "negative_prompt": negative,
            "reference_image_multiple": [],
            "reference_information_extracted_multiple": [],
            "reference_strength_multiple": [],
            "deliberate_euler_ancestral_bug": False,
            "prefer_brownian": True
        }
    }

    headers = {
        "Authorization": f"Bearer {config.api['ai绘画']['nai_key'][int(round_nai)]}",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "content-type": "application/json",
        "dnt": "1",
        "origin": "https://novelai.net",
        "priority": "u=1, i",
        "referer": "https://novelai.net/",
        "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Microsoft Edge";v="132"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
        "x-correlation-id": "89SHW4",
        "x-initiated-at": "2025-01-27T16:40:54.521Z"
    }
    if groupid in no_nsfw_groups and not config.api['ai绘画']['sd审核和反推api']:
        print("审核api未配置,为保证安全已禁止画图请求")
        return "审核api未配置,为保证安全已禁止画图请求"
    if config.api["proxy"]["http_proxy"]:
        proxies = {"http://": config.api["proxy"]["http_proxy"], "https://": config.api["proxy"]["http_proxy"]}
    else:
        proxies = None
    round_nai += 1
    list_length = len(config.api['ai绘画']['nai_key'])
    if round_nai >= list_length:
        round_nai = 0
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
            if groupid in no_nsfw_groups and config.api['ai绘画']['sd审核和反推api']:
                try:
                    check = await pic_audit_standalone(base64.b64encode(image_data).decode('utf-8'), return_none=True,url=config.api['ai绘画']['sd审核和反推api'])
                    if check:
                        return False
                except Exception as e:
                    print(f"审核api失效,为保证安全已禁止画图请求: {e}")
                    return f"审核api失效,为保证安全已禁止画图请求: {e}"
            with open(path, 'wb') as img_file:
                img_file.write(image_data)
    return path


async def n3(prompt, path, groupid, config, args):
    global round_nai
    width = 832
    height = 1216
    url = "https://image.novelai.net"

    if "方" in prompt:
        prompt = prompt.replace("方", "")
        width = 1024
        height = 1024
    if "横" in prompt:
        prompt = prompt.replace("横", "")
        width = 1216
        height = 832
    if "竖" in prompt:
        prompt = prompt.replace("竖", "")
        width = 832
        height = 1216
        
    positive = str(args.get('p', default_args.get('p', positives)) if isinstance(args, dict) and isinstance(default_args, dict) else args.get('p', positives) if isinstance(args, dict) else default_args.get('p', positives) if isinstance(default_args, dict) else positives)
    negative = str(args.get('n', default_args.get('n', negatives)) if isinstance(args, dict) and isinstance(default_args, dict) else args.get('n', negatives) if isinstance(args, dict) else default_args.get('n', negatives) if isinstance(default_args, dict) else negatives)
    positive = (("{}," + positive) if "{}" not in positive else positive).replace("{}", prompt) if isinstance(positive, str) else str(prompt)
    nai_sampler = str(args.get('nai-sampler', default_args.get('nai-sampler', 'k_euler_ancestral')) if isinstance(args, dict) else default_args.get('nai-sampler', 'k_euler_ancestral') if isinstance(default_args, dict) else 'k_euler_ancestral')
    nai_scheduler = str(args.get('nai-scheduler', default_args.get('nai-scheduler', 'karras')) if isinstance(args, dict) else default_args.get('nai-scheduler', 'karras') if isinstance(default_args, dict) else 'karras')
    nai_cfg = float(args.get('nai-cfg', default_args.get('nai-cfg', 5)) if isinstance(args, dict) else default_args.get('nai-cfg', 5) if isinstance(default_args, dict) else 5)

    if groupid in no_nsfw_groups:
        if check_censored(positive, censored_words):
            return False

    payload = {
        "input": positive,
        "model": "nai-diffusion-3",
        "action": "generate",
        "parameters": {
            "params_version": 3,
            "width": width,
            "height": height,
            "scale": 5,
            "sampler": nai_sampler,
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
            "noise_schedule": nai_scheduler,
            "legacy_v3_extend": False,
            "skip_cfg_above_sigma": None,
            "seed": random.randint(0, 2 ** 32 - 1),
            "characterPrompts": [],
            "negative_prompt": negative,
            "reference_image_multiple": [],
            "reference_information_extracted_multiple": [],
            "reference_strength_multiple": []
        }
    }

    headers = {
        "Authorization": f"Bearer {config.api['ai绘画']['nai_key'][int(round_nai)]}",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "content-type": "application/json",
        "dnt": "1",
        "origin": "https://novelai.net",
        "priority": "u=1, i",
        "referer": "https://novelai.net/",
        "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Microsoft Edge";v="132"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
        "x-correlation-id": "89SHW4",
        "x-initiated-at": "2025-01-27T16:40:54.521Z"
    }
    if groupid in no_nsfw_groups and not config.api['ai绘画']['sd审核和反推api']:
        print("审核api未配置,为保证安全已禁止画图请求")
        return "审核api未配置,为保证安全已禁止画图请求"
    if config.api["proxy"]["http_proxy"]:
        proxies = {"http://": config.api["proxy"]["http_proxy"], "https://": config.api["proxy"]["http_proxy"]}
    else:
        proxies = None
    round_nai += 1
    list_length = len(config.api['ai绘画']['nai_key'])
    if round_nai >= list_length:
        round_nai = 0
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
            if groupid in no_nsfw_groups and config.api['ai绘画']['sd审核和反推api']:
                try:
                    check = await pic_audit_standalone(base64.b64encode(image_data).decode('utf-8'), return_none=True,url=config.api['ai绘画']['sd审核和反推api'])
                    if check:
                        return False
                except Exception as e:
                    print(f"审核api失效,为保证安全已禁止画图请求: {e}")
                    return f"审核api失效,为保证安全已禁止画图请求: {e}"
            with open(path, 'wb') as img_file:
                img_file.write(image_data)
    return path


async def SdreDraw(prompt, path, config, groupid, b64_in, args):
    global round_sd
    url = config.api["ai绘画"]["sdUrl"][int(round_sd)]
    args = args
    width = int(args.get('w', sdre_w) if args.get('w', sdre_w) > 0 else sdre_w) if isinstance(args, dict) else sdre_w
    height = int(args.get('h', sdre_h) if args.get('h', sdre_h) > 0 else sdre_h) if isinstance(args, dict) else sdre_h
    denoising_strength = float(
        args.get('d', default_args.get('d', 0.7) if isinstance(default_args, dict) else 0.7) 
        if isinstance(args, dict) else 
        (default_args.get('d', 0.7) if isinstance(default_args, dict) else 0.7)
    )
    steps = min(int(args.get('steps', default_args.get('steps', 15)) if isinstance(args, dict) else default_args.get('steps', 15)) if isinstance(default_args, dict) else 15, 35)

    if "方" in prompt:
        prompt = prompt.replace("方", "")
        width = 1064
        height = 1064
    if "横" in prompt:
        prompt = prompt.replace("横", "")
        width = 1536
        height = 1024
    if "竖" in prompt:
        prompt = prompt.replace("竖", "")
        width = 1024
        height = 1536
    
    if width > 1600:
        width = 1600
    if height > 1600:
        height = 1600

    positive = str(args.get('p', default_args.get('p', positives)) if isinstance(args, dict) and isinstance(default_args, dict) else args.get('p', positives) if isinstance(args, dict) else default_args.get('p', positives) if isinstance(default_args, dict) else positives)
    negative = str(args.get('n', default_args.get('n', negatives)) if isinstance(args, dict) and isinstance(default_args, dict) else args.get('n', negatives) if isinstance(args, dict) else default_args.get('n', negatives) if isinstance(default_args, dict) else negatives)
    positive = (("{}," + positive) if "{}" not in positive else positive).replace("{}", prompt) if isinstance(positive, str) else str(prompt)
    sampler = str(args.get('sampler', default_args.get('sampler', 'Restart')) if isinstance(args, dict) else default_args.get('sampler', 'Restart') if isinstance(default_args, dict) else 'Restart')
    scheduler = str(args.get('scheduler', default_args.get('scheduler', 'Align Your Steps')) if isinstance(args, dict) else default_args.get('scheduler', 'Align Your Steps') if isinstance(default_args, dict) else 'Align Your Steps')
    cfg = float(args.get('cfg', default_args.get('cfg', 6.5)) if isinstance(args, dict) else default_args.get('cfg', 6.5) if isinstance(default_args, dict) else 6.5)

    if groupid in no_nsfw_groups:
        if check_censored(positive, censored_words):
            return False
    
    payload = {
        "init_images": [b64_in],
        "denoising_strength": denoising_strength,
        "enable_hr": 'true',
        "hr_scale": 1.5,
        "hr_second_pass_steps": 15,
        "hr_upscaler": 'SwinIR_4x',
        "prompt": positive,
        "negative_prompt": negative,
        "seed": -1,
        "batch_size": 1,
        "n_iter": 1,
        "steps": steps,
        "save_images": if_save,
        "cfg_scale": cfg,
        "width": width,
        "height": height,
        "restore_faces": False,
        "tiling": False,
        "sampler_name": sampler,
        "scheduler": scheduler,
        "clip_skip_steps": 2,
        "override_settings": {
            "CLIP_stop_at_last_layers": 2,
            "sd_model_checkpoint": ckpt,  # 指定大模型
        },
        "override_settings_restore_afterwards": False,
    }  # manba out
    headers = {
        "Authorization": f"Bearer {config.api['ai绘画']['nai_key'][int(round_nai)]}"
    }
    if groupid in no_nsfw_groups and not config.api['ai绘画']['sd审核和反推api']:
        print("审核api未配置,为保证安全已禁止画图请求")
        return "审核api未配置,为保证安全已禁止画图请求"
    round_sd += 1
    list_length = len(config.api['ai绘画']['sdUrl'])
    if round_sd >= list_length:
        round_sd = 0
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(url=f'{url}/sdapi/v1/img2img', json=payload)
    r = response.json()
    if 'images' not in r or len(r['images']) == 0:
        return None
    # 我的建议是，直接返回base64，让它去审查
    b64 = r['images'][0]
    if groupid in no_nsfw_groups and config.api['ai绘画']['sd审核和反推api']:
        try:
            check = await pic_audit_standalone(b64, return_none=True, url=config.api['ai绘画']['sd审核和反推api'])
            if check:
                return False
        except Exception as e:
            print(f"审核api失效,为保证安全已禁止画图请求: {e}")
            return f"审核api失效,为保证安全已禁止画图请求: {e}"
    image = Image.open(io.BytesIO(base64.b64decode(r['images'][0])))
    # image = Image.open(io.BytesIO(base64.b64decode(p)))
    image.save(f'{path}')
    # image.save(f'{path}')
    return path


async def SdDraw0(prompt, path, config, groupid, args):
    global round_sd
    url = config.api["ai绘画"]["sdUrl"][int(round_sd)]
    args = args
    width = int(args.get('w', sd_w) if args.get('w', sd_w) > 0 else sd_w) if isinstance(args, dict) else sd_w
    height = int(args.get('h', sd_h) if args.get('h', sd_h) > 0 else sd_h) if isinstance(args, dict) else sd_h
    denoising_strength = float(
        args.get('d', default_args.get('d', 0.7) if isinstance(default_args, dict) else 0.7) 
        if isinstance(args, dict) else 
        (default_args.get('d', 0.7) if isinstance(default_args, dict) else 0.7)
    )
    steps = min(int(args.get('steps', default_args.get('steps', 15)) if isinstance(args, dict) else default_args.get('steps', 15)) if isinstance(default_args, dict) else 15, 35)

    if "方" in prompt:
        prompt = prompt.replace("方", "")
        width = 1064
        height = 1064
    if "横" in prompt:
        prompt = prompt.replace("横", "")
        width = 1536
        height = 1024
    if "竖" in prompt:
        prompt = prompt.replace("竖", "")
        width = 1024
        height = 1536
    
    if width > 1600:
        width = 1600
    if height > 1600:
        height = 1600

    positive = str(args.get('p', default_args.get('p', positives)) if isinstance(args, dict) and isinstance(default_args, dict) else args.get('p', positives) if isinstance(args, dict) else default_args.get('p', positives) if isinstance(default_args, dict) else positives)
    negative = str(args.get('n', default_args.get('n', negatives)) if isinstance(args, dict) and isinstance(default_args, dict) else args.get('n', negatives) if isinstance(args, dict) else default_args.get('n', negatives) if isinstance(default_args, dict) else negatives)
    positive = (("{}," + positive) if "{}" not in positive else positive).replace("{}", prompt) if isinstance(positive, str) else str(prompt)
    sampler = str(args.get('sampler', default_args.get('sampler', 'Restart')) if isinstance(args, dict) else default_args.get('sampler', 'Restart') if isinstance(default_args, dict) else 'Restart')
    scheduler = str(args.get('scheduler', default_args.get('scheduler', 'Align Your Steps')) if isinstance(args, dict) else default_args.get('scheduler', 'Align Your Steps') if isinstance(default_args, dict) else 'Align Your Steps')
    cfg = float(args.get('cfg', default_args.get('cfg', 6.5)) if isinstance(args, dict) else default_args.get('cfg', 6.5) if isinstance(default_args, dict) else 6.5)

    if groupid in no_nsfw_groups:
        if check_censored(positive, censored_words):
            return False
    
    payload = {
        "denoising_strength": denoising_strength,
        "enable_hr": 'false',
        "hr_scale": 1.5,
        "hr_second_pass_steps": 15,
        "hr_upscaler": 'SwinIR_4x',
        "prompt": positive,
        "negative_prompt": negative,
        "seed": -1,
        "batch_size": 1,
        "n_iter": 1,
        "steps": steps,
        "save_images": if_save,
        "cfg_scale": cfg,
        "width": width,
        "height": height,
        "restore_faces": False,
        "tiling": False,
        "sampler_name": sampler,
        "scheduler": scheduler,
        "clip_skip_steps": 2,
        "override_settings": {
            "CLIP_stop_at_last_layers": 2,
            "sd_model_checkpoint": ckpt,  # 指定大模型
        },
        "override_settings_restore_afterwards": False,
    }  # manba out
    headers = {
        "Authorization": f"Bearer {config.api['ai绘画']['nai_key'][int(round_nai)]}"
    }
    if groupid in no_nsfw_groups and not config.api['ai绘画']['sd审核和反推api']:
        print("审核api未配置,为保证安全已禁止画图请求")
        return "审核api未配置,为保证安全已禁止画图请求"
    round_sd += 1
    list_length = len(config.api['ai绘画']['sdUrl'])
    if round_sd >= list_length:
        round_sd = 0
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
    print(response)
    print(response.status_code)
    r = response.json()

    b64 = r['images'][0]
    if groupid in no_nsfw_groups and config.api['ai绘画']['sd审核和反推api']:
        try:
            check = await pic_audit_standalone(b64, return_none=True, url=config.api['ai绘画']['sd审核和反推api'])
            if check:
                return False
        except Exception as e:
            print(f"审核api失效,为保证安全已禁止画图请求: {e}")
            return f"审核api失效,为保证安全已禁止画图请求: {e}"
    image = Image.open(io.BytesIO(base64.b64decode(r['images'][0])))
    # image = Image.open(io.BytesIO(base64.b64decode(p)))
    image.save(f'{path}')
    # image.save(f'{path}')
    return path


async def getloras(config):
    global round_sd
    url = f'{config.api["ai绘画"]["sdUrl"][int(round_sd)]}/sdapi/v1/loras'
    headers = {
        "Authorization": f"Bearer {config.api['ai绘画']['nai_key'][int(round_nai)]}"
    }

    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.get(url)
        r = response.json()
        result_lines = [f'<lora:{lora.get("name", "未知")}:1.0>,' for lora in r]
        result = '以下是可用的lora：\n' + '\n'.join(result_lines)
        return result


async def ckpt2(model, config):
    global ckpt
    ckpt = model
    config.settings["ai绘画"]["sd默认启动模型"] = model
    config.save_yaml("settings")


async def getcheckpoints(config):
    global round_sd
    url = f'{config.api["ai绘画"]["sdUrl"][int(round_sd)]}/sdapi/v1/sd-models'
    headers = {
        "Authorization": f"Bearer {config.api['ai绘画']['nai_key'][int(round_nai)]}"
    }

    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.get(url)
        r = response.json()
        model_lines = [f'{model.get("model_name", "未知")}.safetensors' for model in r]
        result = f'当前底模: {ckpt}\n以下是可用的底模：\n' + '\n'.join(model_lines)
        return result

async def n4re0(prompt, path, groupid, config, b64_in, args):
    global round_nai
    width = 1024
    height = 1024
    args = args
    url = "https://image.novelai.net"
    denoising_strength = float(
        args.get('d', default_args.get('d', 0.7) if isinstance(default_args, dict) else 0.7) 
        if isinstance(args, dict) else 
        (default_args.get('d', 0.7) if isinstance(default_args, dict) else 0.7)
    )
    nai_sampler = str(args.get('nai-sampler', default_args.get('nai-sampler', 'k_euler_ancestral')) if isinstance(args, dict) else default_args.get('nai-sampler', 'k_euler_ancestral') if isinstance(default_args, dict) else 'k_euler_ancestral')
    nai_scheduler = str(args.get('nai-scheduler', default_args.get('nai-scheduler', 'karras')) if isinstance(args, dict) else default_args.get('nai-scheduler', 'karras') if isinstance(default_args, dict) else 'karras')
    nai_cfg = float(args.get('nai-cfg', default_args.get('nai-cfg', 5)) if isinstance(args, dict) else default_args.get('nai-cfg', 5) if isinstance(default_args, dict) else 5)

    if "方" in prompt:
        prompt = prompt.replace("方", "")
        width = 1024
        height = 1024
    if "横" in prompt:
        prompt = prompt.replace("横", "")
        width = 1216
        height = 832
    if "竖" in prompt:
        prompt = prompt.replace("竖", "")
        width = 832
        height = 1216

    positive = str(args.get('p', default_args.get('p', positives)) if isinstance(args, dict) and isinstance(default_args, dict) else args.get('p', positives) if isinstance(args, dict) else default_args.get('p', positives) if isinstance(default_args, dict) else positives)
    negative = str(args.get('n', default_args.get('n', negatives)) if isinstance(args, dict) and isinstance(default_args, dict) else args.get('n', negatives) if isinstance(args, dict) else default_args.get('n', negatives) if isinstance(default_args, dict) else negatives)
    positive = (("{}," + positive) if "{}" not in positive else positive).replace("{}", prompt) if isinstance(positive, str) else str(prompt)
    nai_cfg = float(args.get('nai-cfg', default_args.get('nai-cfg', 5)) if isinstance(args, dict) else default_args.get('nai-cfg', 5) if isinstance(default_args, dict) else 5)

    if groupid in no_nsfw_groups:
        if check_censored(positive, censored_words):
            return False

    payload = {
        "input": positive,
        "model": "nai-diffusion-4-curated-preview",
        "action": "img2img",
        "parameters": {
            "params_version": 3,
            "width": width,
            "height": height,
            "scale": nai_cfg,
            "sampler": nai_sampler,
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
            "noise_schedule": nai_scheduler,
            "legacy_v3_extend": False,
            "skip_cfg_above_sigma": None,
            "use_coords": False,
            "seed": random.randint(0, 2 ** 32 - 1),
            "image": b64_in,
            "characterPrompts": [],
            "extra_noise_seed": random.randint(0, 2 ** 32 - 1),
            "v4_prompt": {
                "caption": {
                    "base_caption": positive,
                    "char_captions": []
                },
                "use_coords": False,
                "use_order": True
            },
            "v4_negative_prompt": {
                "caption": {
                    "base_caption": negative,
                    "char_captions": []
                }
            },
            "negative_prompt": negative,
            "reference_image_multiple": [],
            "reference_information_extracted_multiple": [],
            "reference_strength_multiple": [],
            "deliberate_euler_ancestral_bug": False,
            "prefer_brownian": True
        }
    }

    headers = {
        "Authorization": f"Bearer {config.api['ai绘画']['nai_key'][int(round_nai)]}",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "content-type": "application/json",
        "dnt": "1",
        "origin": "https://novelai.net",
        "priority": "u=1, i",
        "referer": "https://novelai.net/",
        "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Microsoft Edge";v="132"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
        "x-correlation-id": "89SHW4",
        "x-initiated-at": "2025-01-27T16:40:54.521Z"
    }
    if config.api["proxy"]["http_proxy"]:
        proxies = {"http://": config.api["proxy"]["http_proxy"], "https://": config.api["proxy"]["http_proxy"]}
    else:
        proxies = None
    if groupid in no_nsfw_groups and not config.api['ai绘画']['sd审核和反推api']:
        print("审核api未配置,为保证安全已禁止画图请求")
        return "审核api未配置,为保证安全已禁止画图请求"
    round_nai += 1
    list_length = len(config.api['ai绘画']['nai_key'])
    if round_nai >= list_length:
        round_nai = 0
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
            if groupid in no_nsfw_groups and config.api['ai绘画']['sd审核和反推api']:
                try:
                    check = await pic_audit_standalone(base64.b64encode(image_data).decode('utf-8'), return_none=True,url=config.api['ai绘画']['sd审核和反推api'])
                    if check:
                        return False
                except Exception as e:
                    print(f"审核api失效,为保证安全已禁止画图请求: {e}")
                    return f"审核api失效,为保证安全已禁止画图请求: {e}"
            with open(path, 'wb') as img_file:
                img_file.write(image_data)
    return path

async def n3re0(prompt, path, groupid, config, b64_in, args):
    global round_nai
    width = 1024
    height = 1024
    args = args
    url = "https://image.novelai.net"
    denoising_strength = float(
        args.get('d', default_args.get('d', 0.7) if isinstance(default_args, dict) else 0.7) 
        if isinstance(args, dict) else 
        (default_args.get('d', 0.7) if isinstance(default_args, dict) else 0.7)
    )
    nai_sampler = str(args.get('nai-sampler', default_args.get('nai-sampler', 'k_euler_ancestral')) if isinstance(args, dict) else default_args.get('nai-sampler', 'k_euler_ancestral') if isinstance(default_args, dict) else 'k_euler_ancestral')
    nai_scheduler = str(args.get('nai-scheduler', default_args.get('nai-scheduler', 'karras')) if isinstance(args, dict) else default_args.get('nai-scheduler', 'karras') if isinstance(default_args, dict) else 'karras')
    nai_cfg = float(args.get('nai-cfg', default_args.get('nai-cfg', 5)) if isinstance(args, dict) else default_args.get('nai-cfg', 5) if isinstance(default_args, dict) else 5)

    if "方" in prompt:
        prompt = prompt.replace("方", "")
        width = 1024
        height = 1024
    if "横" in prompt:
        prompt = prompt.replace("横", "")
        width = 1216
        height = 832
    if "竖" in prompt:
        prompt = prompt.replace("竖", "")
        width = 832
        height = 1216

    positive = str(args.get('p', default_args.get('p', positives)) if isinstance(args, dict) and isinstance(default_args, dict) else args.get('p', positives) if isinstance(args, dict) else default_args.get('p', positives) if isinstance(default_args, dict) else positives)
    negative = str(args.get('n', default_args.get('n', negatives)) if isinstance(args, dict) and isinstance(default_args, dict) else args.get('n', negatives) if isinstance(args, dict) else default_args.get('n', negatives) if isinstance(default_args, dict) else negatives)
    positive = (("{}," + positive) if "{}" not in positive else positive).replace("{}", prompt) if isinstance(positive, str) else str(prompt)

    if groupid in no_nsfw_groups:
        if check_censored(positive, censored_words):
            return False

    payload = {
        "input": positive,
        "model": "nai-diffusion-3",
        "action": "img2img",
        "parameters": {
            "params_version": 3,
            "width": width,
            "height": height,
            "scale": nai_cfg,
            "sampler": nai_sampler,
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
            "noise_schedule": nai_scheduler,
            "legacy_v3_extend": False,
            "skip_cfg_above_sigma": None,
            "use_coords": False,
            "seed": random.randint(0, 2 ** 32 - 1),
            "image": b64_in,
            "characterPrompts": [],
            "extra_noise_seed": random.randint(0, 2 ** 32 - 1),
            "negative_prompt": negative,
            "reference_image_multiple": [],
            "reference_information_extracted_multiple": [],
            "reference_strength_multiple": [],
            "deliberate_euler_ancestral_bug": False,
            "prefer_brownian": True
        }
    }

    headers = {
        "Authorization": f"Bearer {config.api['ai绘画']['nai_key'][int(round_nai)]}",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "content-type": "application/json",
        "dnt": "1",
        "origin": "https://novelai.net",
        "priority": "u=1, i",
        "referer": "https://novelai.net/",
        "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Microsoft Edge";v="132"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
        "x-correlation-id": "89SHW4",
        "x-initiated-at": "2025-01-27T16:40:54.521Z"
    }
    if config.api["proxy"]["http_proxy"]:
        proxies = {"http://": config.api["proxy"]["http_proxy"], "https://": config.api["proxy"]["http_proxy"]}
    else:
        proxies = None
    if groupid in no_nsfw_groups and not config.api['ai绘画']['sd审核和反推api']:
        print("审核api未配置,为保证安全已禁止画图请求")
        return "审核api未配置,为保证安全已禁止画图请求"
    round_nai += 1
    list_length = len(config.api['ai绘画']['nai_key'])
    if round_nai >= list_length:
        round_nai = 0
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
            if groupid in no_nsfw_groups and config.api['ai绘画']['sd审核和反推api']:
                try:
                    check = await pic_audit_standalone(base64.b64encode(image_data).decode('utf-8'), return_none=True,url=config.api['ai绘画']['sd审核和反推api'])
                    if check:
                        return False
                except Exception as e:
                    print(f"审核api失效,为保证安全已禁止画图请求: {e}")
                    return f"审核api失效,为保证安全已禁止画图请求: {e}"
            with open(path, 'wb') as img_file:
                img_file.write(image_data)
    return path

async def SdmaskDraw(prompt, path, config, groupid, b64_in, args, mask_base64):
    global round_sd
    url = config.api["ai绘画"]["sdUrl"][int(round_sd)]
    args = args
    width = int(args.get('w', sdre_w) if args.get('w', sdre_w) > 0 else sdre_w) if isinstance(args, dict) else sdre_w
    height = int(args.get('h', sdre_h) if args.get('h', sdre_h) > 0 else sdre_h) if isinstance(args, dict) else sdre_h
    denoising_strength = float(
        args.get('d', default_args.get('d', 0.7) if isinstance(default_args, dict) else 0.7) 
        if isinstance(args, dict) else 
        (default_args.get('d', 0.7) if isinstance(default_args, dict) else 0.7)
    )
    steps = min(int(args.get('steps', default_args.get('steps', 15)) if isinstance(args, dict) else default_args.get('steps', 15)) if isinstance(default_args, dict) else 15, 35)

    if "方" in prompt:
        prompt = prompt.replace("方", "")
        width = 1064
        height = 1064
    if "横" in prompt:
        prompt = prompt.replace("横", "")
        width = 1536
        height = 1024
    if "竖" in prompt:
        prompt = prompt.replace("竖", "")
        width = 1024
        height = 1536
    
    if width > 1600:
        width = 1600
    if height > 1600:
        height = 1600

    positive = str(args.get('p', default_args.get('p', positives)) if isinstance(args, dict) and isinstance(default_args, dict) else args.get('p', positives) if isinstance(args, dict) else default_args.get('p', positives) if isinstance(default_args, dict) else positives)
    negative = str(args.get('n', default_args.get('n', negatives)) if isinstance(args, dict) and isinstance(default_args, dict) else args.get('n', negatives) if isinstance(args, dict) else default_args.get('n', negatives) if isinstance(default_args, dict) else negatives)
    positive = (("{}," + positive) if "{}" not in positive else positive).replace("{}", prompt) if isinstance(positive, str) else str(prompt)
    sampler = str(args.get('sampler', default_args.get('sampler', 'Restart')) if isinstance(args, dict) else default_args.get('sampler', 'Restart') if isinstance(default_args, dict) else 'Restart')
    scheduler = str(args.get('scheduler', default_args.get('scheduler', 'Align Your Steps')) if isinstance(args, dict) else default_args.get('scheduler', 'Align Your Steps') if isinstance(default_args, dict) else 'Align Your Steps')
    cfg = float(args.get('cfg', default_args.get('cfg', 6.5)) if isinstance(args, dict) else default_args.get('cfg', 6.5) if isinstance(default_args, dict) else 6.5)

    if groupid in no_nsfw_groups:
        if check_censored(positive, censored_words):
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
        "prompt": positive,
        "negative_prompt": negative,
        "seed": -1,
        "batch_size": 1,
        "n_iter": 1,
        "steps": steps,
        "save_images": if_save,
        "cfg_scale": cfg,
        "width": width,
        "height": height,
        "restore_faces": False,
        "tiling": False,
        "sampler_name": sampler,
        "scheduler": scheduler,
        "clip_skip_steps": 2,
        "override_settings": {
            "CLIP_stop_at_last_layers": 2,
            "sd_model_checkpoint": ckpt,  # 指定大模型
        },
        "override_settings_restore_afterwards": False,
    }  # manba out
    headers = {
        "Authorization": f"Bearer {config.api['ai绘画']['nai_key'][int(round_nai)]}"
    }
    if groupid in no_nsfw_groups and not config.api['ai绘画']['sd审核和反推api']:
        print("审核api未配置,为保证安全已禁止画图请求")
        return "审核api未配置,为保证安全已禁止画图请求"
    round_sd += 1
    list_length = len(config.api['ai绘画']['sdUrl'])
    if round_sd >= list_length:
        round_sd = 0
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(url=f'{url}/sdapi/v1/img2img', json=payload)
    r = response.json()
    if 'images' not in r or len(r['images']) == 0:
        return None
    # 我的建议是，直接返回base64，让它去审查
    b64 = r['images'][0]
    if groupid in no_nsfw_groups and config.api['ai绘画']['sd审核和反推api']:
        try:
            check = await pic_audit_standalone(b64, return_none=True, url=config.api['ai绘画']['sd审核和反推api'])
            if check:
                return False
        except Exception as e:
            print(f"审核api失效,为保证安全已禁止画图请求: {e}")
            return f"审核api失效,为保证安全已禁止画图请求: {e}"
    image = Image.open(io.BytesIO(base64.b64decode(r['images'][0])))
    # image = Image.open(io.BytesIO(base64.b64decode(p)))
    image.save(f'{path}')
    # image.save(f'{path}')
    return path

async def getsampler(config):
    global round_sd
    url = f'{config.api["ai绘画"]["sdUrl"][int(round_sd)]}/sdapi/v1/samplers'
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.get(url)
        r = response.json()
        names_list = [item["name"] for item in r if "name" in item]
        result = f'\n'.join(names_list)
        return result
    
async def getscheduler(config):
    global round_sd
    url = f'{config.api["ai绘画"]["sdUrl"][int(round_sd)]}/sdapi/v1/schedulers'
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.get(url)
        r = response.json()
        label_list = [item["label"] for item in r if "label" in item]
        result = f'\n'.join(label_list)
        return result

async def interrupt(config):
    global round_sd
    try:
        adjusted_index = int(round_sd) - 1
        sdUrls = config.api["ai绘画"]["sdUrl"]
        if adjusted_index < 0 or adjusted_index >= len(sdUrls):
            raise IndexError("索引超出范围，请检查 round_sd 的值。")
        url = f'{sdUrls[adjusted_index]}/sdapi/v1/interrupt'
        post_data = {
            "114514": "1919810"
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=post_data)
            response.raise_for_status()
            return response.json()
    except (ValueError, IndexError) as e:
        print(f"参数错误: {e}")
        return None
    except httpx.HTTPError as e:
        print(f"请求失败: {e}")
        return None
    
async def skipsd(config):
    global round_sd
    try:
        adjusted_index = int(round_sd) - 1
        sdUrls = config.api["ai绘画"]["sdUrl"]
        if adjusted_index < 0 or adjusted_index >= len(sdUrls):
            raise IndexError("索引超出范围，请检查 round_sd 的值。")
        url = f'{sdUrls[adjusted_index]}/sdapi/v1/skip'
        post_data = {
            "114514": "1919810"
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=post_data)
            response.raise_for_status()
            return response.json()
    except (ValueError, IndexError) as e:
        print(f"参数错误: {e}")
        return None
    except httpx.HTTPError as e:
        print(f"请求失败: {e}")
        return None
