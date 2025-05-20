plugin_description="群聊娱乐功能"
dynamic_imports ={
    "run.group_fun.func_collection": ["random_ninjutsu","query_ninjutsu"],
}
function_declarations=[
    {
        "name": "query_ninjutsu",
        "description": "查询忍术",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "忍术名称"
                },
            },
            "required": [
                "name"
            ]
        }
    },
    {
        "name": "random_ninjutsu",
        "description": "随机获取忍术",
    }
]