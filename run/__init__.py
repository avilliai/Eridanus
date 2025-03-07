dynamic_imports = {
    "run.basic_plugin": [
        "call_weather_query", "call_setu", "call_image_search",
        "call_tts", "call_tarot", "call_pick_music",
        "call_fortune", "call_all_speakers","call_quit_chat"
    ],
    "run.user_data": [
        "call_user_data_register", "call_user_data_query", "call_user_data_sign",
        "call_change_city", "call_change_name", "call_permit",
        "call_delete_user_history", "call_clear_all_history"
    ],
    "run.aiDraw": ["call_text2img", "call_aiArtModerate"],
}
function_declarations=[
    {
        "name": "call_weather_query",
        "description": "Get the current weather in a given location.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. 上海"
                }
            },
            "required": [
                "location"
            ]
        }
    },
    {
        "name": "call_setu",
        "description": "根据关键词搜索相关图片并返回图片。",
        "parameters": {
            "type": "object",
            "properties": {
                "tags": {
                    "type": "array",
                    "description": "所要求的关键词。eg.白丝 萝莉",
                    "items": {
                        "type": "string"
                    }
                },
                "num": {
                    "type": "integer",
                    "description": "返回的图片数量。默认为1"
                }
            },
            "required": [
                "tags"
            ]
        }
    },
    {
        "name": "call_image_search",
        "description": "按照用户要求搜索给定图片的来源，当且仅当用户要求搜索时才可触发。",
        "parameters": {
            "type": "object",
            "properties": {
                "image_url": {
                    "type": "string",
                    "description": "图片的url"
                }
            },
            "required": [
                "image_url"
            ]
        }
    },
    {
        "name": "call_tts",
        "description": "根据文本和语音合成角色，合成语音并播放。",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "要合成的文本。"
                },
                "speaker": {
                    "type": "string",
                    "description": "使用的语音合成角色。默认角色为None"
                },
                "mood": {
                    "type": "string",
                    "enum": ["生气_angry", "开心_happy", "中立_neutral", "难过_sad"],
                    "description": "语音的情绪。根据具体句子判断。"
                }
            },
            "required": [
                "text"
            ]
        }
    },
    {
        "name": "call_pick_music",
        "description": "触发音乐选取功能。根据歌曲名或歌手名搜索点歌。",
        "parameters": {
            "type": "object",
            "properties": {
                "aim": {
                    "type": "string",
                    "description": "歌曲名、歌手名或者二者混合。eg.周杰伦 eg.屋顶 eg.周杰伦 屋顶"
                }
            },
            "required": [
                "aim"
            ]
        }
    },
    {
        "name": "call_tarot",
        "description": "抽取一张塔罗牌。"
    },
    {
        "name": "call_fortune",
        "description": "运势占卜，返回图片。"
    },
    {
        "name": "call_all_speakers",
        "description": "获取可用的语音合成角色列表。"
    },
    {
        "name": "call_delete_user_history",
        "description": "清理当前对话记录"
    },
    {
        "name": "call_clear_all_history",
        "description": "清理所有用户的对话记录"
    },

    {
        "name": "call_quit_chat",
        "description": "停止对话，不再接收信息"
    },

    {
        "name": "call_user_data_register",
        "description": "在数据库中注册用户"
    },
    {
        "name": "call_user_data_query",
        "description": "查询用户数据。eg.权限等级等内容。"
    },
    {
        "name": "call_user_data_sign",
        "description": "签到。实现签到行为。"
    },
    {
        "name": "call_change_city",
        "description": "调整所在城市信息。eg：修改城市为新乡",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "用户所在的城市。eg：新乡"
                }
            },
            "required": [
                "city"
            ]
        }
    },
    {
        "name": "call_change_name",
        "description": "改变称呼。触发示例： 叫我阿明",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "称呼"
                }
            },
            "required": [
                "name"
            ]
        }
    },
    {
        "name": "call_permit",
        "description": "授权",
        "parameters": {
            "type": "object",
            "properties": {
                "target_id": {
                    "type": "integer",
                    "description": "所要授权的对象的qq号码/群的群号"
                },
                "level": {
                    "type": "integer",
                    "description": "授权等级。1为最低，数字越大权限越高"
                },
                "type": {
                    "type": "string", "enum": ["user", "group"], "description": "授权对象类型。user为qq号码，group为群号"
                }
            },
            "required": [
                "target_id",
                "level",
                "type"
            ]
        }
    },
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
