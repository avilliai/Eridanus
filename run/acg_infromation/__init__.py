dynamic_imports={
    "run.acg_infromation.bangumi": ["call_bangumi_search"],
    "run.acg_infromation.character_identify": ["call_character_identify"],
}
function_declarations=[
    {
        "name": "call_bangumi_search",
        "description": "搜索acg相关番剧、动画、小说、游戏、音乐、三次元人物等",
        "parameters": {
            "type": "object",
            "properties": {
                "cat": {
                    "type": "string", "enum": ["番剧", "动画", "书籍", "游戏", "音乐", "三次元人物"],
                    "description": "搜索类型"
                },
                "keywords": {
                    "type": "string",
                    "description": "搜索关键词"
                }
            },
            "required": [
                "keywords"
            ]
        }
    },
    {
        "name": "call_character_identify",
        "description": "按照用户要求识别图片中的人物",
        "parameters": {
            "type": "object",
            "properties": {
                "image_url": {
                    "type": "string",
                    "description": "图片的url"
                },
                "model_name": {
                    "type": "string", "enum": ["anime_model_lovelive", "game_model_kirakira"],
                    "description": "game_model_kirakira为galgame游戏角色识别，anime_model_lovelive为动漫角色识别"
                }
            },
            "required": [
                "image_url",
                "model_name"
            ]
        }
    },
]