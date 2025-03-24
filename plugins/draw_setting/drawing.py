import random
import ssl
from PIL import Image as iMG
import httpx
from urllib import request
import json
import os
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
      "model": "wd-vit-tagger-v3",
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
    prompt["3"]["inputs"]["seed"] = random.randint(1,999999999999999)
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