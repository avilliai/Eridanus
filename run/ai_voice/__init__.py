plugin_description="语音合成"

dynamic_imports = {
    "run.ai_voice.text2voice": [
        "call_tts", "call_all_speakers"]
}
function_declarations=[
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
        "name": "call_all_speakers",
        "description": "获取可用的语音合成角色列表。"
    },

]
