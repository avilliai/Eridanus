dynamic_imports={
    "run.anime_game_service.func_collection":[
        "anime_game_service_func_collection"
    ],
}
function_declarations=[
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