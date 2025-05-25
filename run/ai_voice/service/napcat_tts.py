
async def napcat_tts_speakers(bot):
    try:
        nc_speakers = await bot.get_ai_characters()
        #print(nc_speakers)
        speakers = {}
        for type in nc_speakers["data"]:
            for speaker in type["characters"]:
                speakers[speaker["character_name"]]=speaker["character_id"]

        #print(speakers)
        return speakers
    except Exception as e:
        return None
async def napcat_tts_speak(bot,config, text, speaker_id):
    try:
        s = await bot.get_ai_record(config.common_config.basic_config["group"],speaker_id, text=text)
        return s["data"]
    except Exception as e:
        return None