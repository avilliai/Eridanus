dynamic_imports = {
    "run.basic_plugin": [
        "call_weather_query", "call_setu", "call_image_search",
        "call_tts", "call_tarot", "call_pick_music",
        "call_fortune", "call_all_speakers"
    ],
    "run.user_data": [
        "call_user_data_register", "call_user_data_query", "call_user_data_sign",
        "call_change_city", "call_change_name", "call_permit",
        "call_delete_user_history", "call_clear_all_history"
    ],
    "run.aiDraw": ["call_text2img", "call_aiArtModerate"],
}