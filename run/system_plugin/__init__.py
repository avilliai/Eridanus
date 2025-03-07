dynamic_imports = {
    "run.system_plugin.func_collection": ["operate_group_push_tasks"],
    "run.system_plugin.Mface_Record": ["call_send_mface"]
}
function_declarations=[
    {
        "name": "operate_group_push_tasks",
        "description": "添加或取消推送任务",
        "parameters": {
            "type": "object",
            "properties": {
                "task_type": {
                    "type": "string", "enum": ["asmr", "bilibili"], "description": "任务类型: asmr/b站动态 "
                },
                "operation": {
                    "type": "boolean",
                    "description": "true为添加，false为取消"
                },
                "target_uid": {
                    "type": "integer",
                    "description": "b站动态订阅，目标uid"
                }
            },
            "required": [
                "task_type",
                "operation"
            ]
        }
    },
]