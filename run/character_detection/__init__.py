plugin_description="图片审核"
dynamic_imports={
    "run.character_detection.func_collection": ["operate_group_censor"],
}
function_declarations=[
    {
        "name": "operate_group_censor",
        "description": "开启或关闭奶龙审核或doro或男娘图片审核",
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string", "enum": ["开启奶龙审核", "关闭奶龙审核", "开启doro审核", "关闭doro审核", "开启男娘审核", "关闭男娘审核"],
                    "description": "开启或关闭奶龙或doro审核。"
                },
                "target_id": {
                    "type": "integer",
                    "description": "要操作的目标群号"
                }
            },
            "required": [
                "operation",
                "target_id"
            ]
        }
    },
]
