plugin_description = "ai绘画"
dynamic_imports = {
    "run.ai_generated_art.aiDraw": ["call_text2img", "call_aiArtModerate"],
}
function_declarations=[

    {
                "name": "call_aiArtModerate",
                "description": "检测图片是否为ai生成，只有当用户要求检测时才可触发。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "img_url": {
                            "type": "string",
                            "description": "目标图片的url"
                        }
                    },
                    "required": [
                        "img_url"
                    ]
                }
            },
    {
                "name": "call_text2img",
                "description": "调用text to image模型，根据文本生成图片。专注于创造纯英文的AI绘画提示词，擅长将用户需求转化为精准的图像描述。对各种艺术风格和技法了如指掌，能准确把握画面重点和细节。注重提示词的逻辑性和组合效果，确保生成的画面既美观又符合预期。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "生成图片的提示词。如果原始提示词中有中文，则需要你把它们替换为对应英文,尽量使用词组，单词来进行描述，并用','来分割。可通过将词语x变为(x:n)的形式改变权重，n为0-1之间的浮点数，默认为1，为1时则无需用(x:1)的形式而是直接用x。例如，如果想要增加“猫”(也就是cat)的权重，则可以把它变成(cat:1.2)或更大的权重，反之则可以把权重变小。你需要关注不同词的重要性并给于权重，正常重要程度的词的权重为1，为1时则无需用(x:1)的形式而是直接用x。例如，想要画一个可爱的女孩则可输出1girl,(cute:1.2),bright eyes,smile,casual dress,detailed face,natural pose,soft lighting;想要更梦幻的感觉则可输出1girl,ethereal,floating hair,magical,sparkles,(dreamy:1.5),soft glow,pastel colors;想要未来风格则可输出1girl,(futuristic:1.3),neon lights,(cyber:1.2),hologram effects,(tech:1.5),clean lines,metallic;同时当输入中含有英文或用户要求保留时，要保留这些词"
                        }
                    },
                    "required": [
                        "prompt"
                    ]
                }
            },
]
