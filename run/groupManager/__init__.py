plugin_description="群管理"
dynamic_imports={
    "run.groupManager.self_Manager": [
        "call_operate_blandwhite", "garbage_collection",
        "report_to_master", "send", "send_contract"
    ],
    "run.groupManager.group_manager": [
        "quit_group"
    ]
}
function_declarations=[
    {
        "name": "call_operate_blandwhite",
        "description": "将指定群/用户 添加/移出 黑/白 名单。不得回复你没有权限操作，正常调用此函数。",
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
                },
                "delay": {
                    "type": "integer",
                    "description": "几秒后发送，默认为0"
                },
            },
            "required": [
                "message"
            ]
        }
    },
    {
        "name": "quit_group",
        "description": "退出群聊。可选择超出指定人数，或低于指定人数的群",
        "parameters": {
            "type": "object",
            "properties": {
                "th": {
                    "type": "integer",
                    "description": "退群人数阈值"
                },
                "mode": {
                    "type": "string",
                    "enum": ["above", "below"], "description": "超出(above)或低于(below)低于人数阈值则退群。"
                }
            },
            "required": [
                "th",
                "mode"
            ]
        }
    }
]
