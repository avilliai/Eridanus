import asyncio
import random
import ssl
from PIL import Image as iMG
import httpx
from asyncio import Lock
from urllib import request
import json
import os
from developTools.message.message_components import Image, Text
from plugins.random_pic.random_anime import get_text_number
base_model = {"has":'hassakuXLIllustrious_v21.safetensors',"jru":'jruTheJourneyRemains_v27.safetensors',"obs":'obsessionIllustrious_vPredV11.safetensors',
              "waiN":'waiNSFWIllustrious_v120.safetensors',"waiS":'waiSHUFFLENOOB_vPred20.safetensors',"mis":'mistoonAnimeNoobai.CS46.safetensors',
              "alc":'alchemix20illustrious.lAYX.safetensors',"any":'AnythingXL_xl.safetensors'}
random_model = random.choice(list(base_model.values()))
model_list = ", ".join(f"{k}: {v}" for k, v in base_model.items())
prompt_text ='''
{
  "3": {
    "inputs": {
      "seed": 332854275159177,
      "steps": 4,
      "cfg": 1,
      "sampler_name": "euler",
      "scheduler": "simple",
      "denoise": 1,
      "model": [
        "18",
        0
      ],
      "positive": [
        "6",
        0
      ],
      "negative": [
        "7",
        0
      ],
      "latent_image": [
        "5",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "K采样器"
    }
  },
  "4": {
    "inputs": {
      "ckpt_name": "waiNSFWIllustrious_v120.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Checkpoint加载器（简易）"
    }
  },
  "5": {
    "inputs": {
      "width": 1024,
      "height": 1600,
      "batch_size": 3
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "空Latent图像"
    }
  },
  "6": {
    "inputs": {
      "text": [
        "17",
        0
      ],
      "clip": [
        "18",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP文本编码"
    }
  },
  "7": {
    "inputs": {
      "text": "embedding:badhandv4,bad anatomy,blurry,(worst quality:1.8),low quality,hands bad,face bad,(normal quality:1.3),bad hands,mutated hands and fingers,extra legs,extra arms,duplicate,cropped,text,jpeg,artifacts,signature,watermark,username,blurry,artist name,trademark,title,multiple view,Reference sheet,long body,multiple breasts,mutated,bad anatomy,disfigured,bad proportions,duplicate,bad feet,artist name,ugly,text font ui,missing limb,monochrome,chromatic aberration, signature, extra digits, artistic error, username, scan, [abstract], signature, artist name,extra fingers,fingers,",
      "clip": [
        "18",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP文本编码"
    }
  },
  "8": {
    "inputs": {
      "samples": [
        "3",
        0
      ],
      "vae": [
        "4",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE解码"
    }
  },
  "9": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": [
        "8",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "保存图像"
    }
  },
  "10": {
    "inputs": {
      "lora_name": "add_detail.safetensors",
      "strength_model": 4,
      "strength_clip": 1,
      "model": [
        "11",
        0
      ],
      "clip": [
        "11",
        1
      ]
    },
    "class_type": "LoraLoader",
    "_meta": {
      "title": "加载LoRA"
    }
  },
  "11": {
    "inputs": {
      "lora_name": "USNR_STYLE_ILL_V1_lokr3-000024.safetensors",
      "strength_model": 1,
      "strength_clip": 1.01,
      "model": [
        "4",
        0
      ],
      "clip": [
        "4",
        1
      ]
    },
    "class_type": "LoraLoader",
    "_meta": {
      "title": "加载LoRA"
    }
  },
  "16": {
    "inputs": {
      "image": "undefined"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "加载图像"
    }
  },
  "17": {
    "inputs": {
      "model": "wd-eva02-large-tagger-v3",
      "threshold": 0.35,
      "character_threshold": 0.85,
      "replace_underscore": true,
      "trailing_comma": false,
      "exclude_tags": "",
      "tags": "1 beautiful girl,",
      "image": [
        "16",
        0
      ]
    },
    "class_type": "WD14Tagger|pysssss",
    "_meta": {
      "title": "WD14 Tagger 🐍"
    }
  },
  "18": {
    "inputs": {
      "lora_name": "checkpoint-e18_s306.safetensors",
      "strength_model": 0.8,
      "strength_clip": 1,
      "model": [
        "19",
        0
      ],
      "clip": [
        "19",
        1
      ]
    },
    "class_type": "LoraLoader",
    "_meta": {
      "title": "加载LoRA"
    }
  },
  "19": {
    "inputs": {
      "lora_name": "wai-Rectified-s.safetensors",
      "strength_model": 1,
      "strength_clip": 1,
      "model": [
        "10",
        0
      ],
      "clip": [
        "10",
        1
      ]
    },
    "class_type": "LoraLoader",
    "_meta": {
      "title": "加载LoRA"
    }
  }
}
'''

input_path = 'C:/Users/29735/Desktop/project/ComfyUI_windows_portable/ComfyUI/input'
output_path = 'C:/Users/29735/Desktop/project/ComfyUI_windows_portable/ComfyUI/output'
def get_prompt():
    prompt = json.loads(prompt_text)
    #prompt["17"]["inputs"]["tags"] += (','+random.randint(1,999999999999999))
    return prompt,input_path,output_path

def delete_files(directory):
    file_list = os.listdir(directory)
    for file in file_list:
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

    # Create a JSON payload with the prompt
def get_images(prompt):
    p = {"prompt": prompt}
    # Create a request object with the payload
    data = json.dumps(p).encode('utf-8')
    # Send the request and get the response
    req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
    request.urlopen(req)

async def extract_first_frame(gif_path, output_path):
    with iMG.open(gif_path) as img:
        first_frame = img.convert("RGBA")  # 确保兼容性
        first_frame.save(output_path)

async def download_image(url, output_file):
    # 创建自定义 SSL 配置
    ssl_context = ssl.create_default_context()
    ssl_context.set_ciphers("DEFAULT:@SECLEVEL=0")  # 降低安全级别，允许旧协议
    ssl_context.check_hostname = False  # 不检查域名匹配
    ssl_context.verify_mode = ssl.CERT_NONE  # 跳过证书验证

    # 使用 httpx 自定义传输
    transport = httpx.AsyncHTTPTransport(verify=ssl_context)

    async with httpx.AsyncClient(transport=transport, timeout=30.0) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()  # 确保请求成功
            with open(output_file, "wb") as file:
                file.write(response.content)
            print(f"图片下载成功: {output_file}")
        except httpx.HTTPStatusError as e:
            print(f"HTTP 错误: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            print(f"请求错误: {e}")
        except Exception as e:
            print(f"发生未知错误: {e}")
    await extract_first_frame(output_file, output_file)
    width, height = iMG.open(output_file).size
    return width, height

async def draw(bot,config,draw_waiting_queue,draw_group_id,prompt,lock=Lock()):
  async with lock:
    info = await draw_waiting_queue.get()
    group_id = await draw_group_id.get()
    txt = info.get(Text)[0].text
    numbers = await get_text_number(bot,config,txt)
    lst = []
    if 'random' in txt:
      prompt["4"]["inputs"]["ckpt_name"] = random_model
    #绘画模式
    if txt.startswith('draw'):
      text = txt.split('-')[2]
      prompt["6"]["inputs"]["text"] = text + ',' + str(random.randint(1,999999999999999))
    #重画模式
    if txt.startswith('重画'):
      prompt["6"]["inputs"]["text"] =  ["17",0]
      image_url = info.get(Image)[0].url
      image_name = image_url.split('/')[-1][-25:]+'.png'
      image_path = os.path.join(input_path, image_name)
      lst = [Text('原图：'),Image(file=image_path)]
      width, height = await download_image(image_url, image_path)
      #height, width = cv2.imread(image_path+'.png').shape[:2]
      if 1028< height < 1600:
        prompt["5"]["inputs"]["height"] = height
      if 760< width < 1152:
        prompt["5"]["inputs"]["width"] = width
      prompt["16"]["inputs"]["image"] = image_name
    if prompt["4"]["inputs"]["ckpt_name"] == base_model['mis'] or prompt["4"]["inputs"]["ckpt_name"] == base_model['any']:
      prompt["5"]["inputs"]["height"] = 1000
      prompt["5"]["inputs"]["width"] = 896
    bot.logger.info("画图!")            
    #prompt["4"]["inputs"]["ckpt_name"] = random_model
    prompt["5"]["inputs"]["batch_size"] = numbers
    prompt["3"]["inputs"]["seed"] = random.randint(1,999999999999999)
    #delete_files(output_path)
    prompt["17"]["inputs"]["tags"] += str(random.randint(1,999999999999999))
    get_images(prompt)
    file_list = os.listdir(output_path)
    ori_file_len = len(file_list)
    while len(file_list) < ori_file_len + numbers:
        await asyncio.sleep(0.85)
        file_list = os.listdir(output_path)
    asyncio.sleep(0.05)
    for file in file_list[-1:-numbers-1:-1]:
        if file.endswith('.png'):
          img_path = os.path.join(output_path, file)
          lst.append(Image(file=img_path))
    bot.logger.info('start sending')
    #await bot.send_group_message(group_id,Node(content=lst))
  return lst

async def get_model_list(prompt,model_list=model_list):
    info = '模型列表：\n'+model_list+'当前模型：'+prompt["4"]["inputs"]["ckpt_name"]+'\n切换模型请按模式：模型切换 模型名(key)'
    return info, base_model
