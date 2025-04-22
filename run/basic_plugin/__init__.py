dynamic_imports = {
    "run.basic_plugin": [
        "call_weather_query", "call_setu", "call_image_search",
        "call_tts", "call_tarot", "call_pick_music",
        "call_fortune", "call_all_speakers","call_quit_chat"
    ],
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
        "name": "call_quit_chat",
        "description": "停止对话，不再接收信息"
    },


]
