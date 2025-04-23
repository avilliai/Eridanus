plugin_description="ACG相关信息查询插件"
dynamic_imports={
    "run.acg_infromation.bangumi": ["call_bangumi_search"],
    "run.acg_infromation.character_identify": ["call_character_identify"],
    "run.acg_infromation.func_collection": [
        "anime_game_service_func_collection"
    ],
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
                    "type": "string", "enum": ["anime_model_lovelive", "full_game_model_kira"],
                    "description": "full_game_model_kira为galgame游戏角色识别，anime_model_lovelive为动漫角色识别"
                }
            },
            "required": [
                "image_url",
                "model_name"
            ]
        }
    },
    {
        "name": "anime_game_service_func_collection",
        "description": "调用游戏查询服务的功能集合。",
        "parameters": {
            "type": "object",
            "properties": {
                "m_type": {
                    "type": "string", "enum": ["blue_archive", "steam"],
                    "description": "blue_archive：碧蓝档案游戏攻略查询(角色、关卡) ；steam：Steam游戏查询"
                },
                "query_target": {
                    "type": "string",
                    "description": "查询目标，如游戏名称、游戏角色名称等"
                }
            },
            "required": [
                "m_type",
                "query_target"
            ]
        }
    },
]
