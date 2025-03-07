dynamic_imports={
    "run.groupManager.self_Manager": [
        "call_operate_blandwhite", "garbage_collection",
        "report_to_master", "send", "send_contract"
    ],
    "run.groupManager.nailong_get": ["operate_group_censor"],
}
function_declarations=[
    {
        "name": "call_operate_blandwhite",
        "description": "添加或删除用户/群的白名单/黑名单。",
        "parameters": {
            "type": "object",
            "properties": {
                "target_id": {
                    "type": "integer",
                    "description": "要操作的目标id"
                },
                "type": {
                    "type": "string",
                    "enum": ["添加群黑名单", "取消群黑名单", "添加用户黑名单", "取消用户黑名单", "添加用户白名单",
                             "取消用户白名单", "添加群白名单", "取消群白名单"], "description": "操作类型"
                }
            },
            "required": [
                "target_id",
                "type"
            ]
        }
    },
    {
        "name": "garbage_collection",
        "description": "清理运行所产生的垃圾文件。"
    },
    {
        "name": "report_to_master",
        "description": "向管理员(master)上报用户的恶性行为。当bot接受到任何攻击性言论、侮辱性言论、骚扰言论时触发。或是用户需要向管理员反馈时触发。"
    },
    {
        "name": "send_contract",
        "description": "发送管理员的联系方式"
    },
    {
        "name": "send",
        "description": "根据要求发送消息，参数从上下文中获取。",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "array",
                    "description": "消息内容",
                    "items": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "文本内容"
                            },
                            "image": {
                                "type": "string",
                                "description": "图片url或path"
                            },
                            "audio": {
                                "type": "string",
                                "description": "音频url或path"
                            },
                            "video": {
                                "type": "string",
                                "description": "视频url或path"
                            }
                        }
                    }
                }
            },
            "required": [
                "message"
            ]
        }
    },
    {
        "name": "operate_group_censor",
        "description": "开启或关闭奶龙审核或doro图片审核",
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string", "enum": ["开启奶龙审核", "关闭奶龙审核", "开启doro审核", "关闭doro审核"],
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