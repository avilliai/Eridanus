import traceback

from developTools.event.events import GroupMessageEvent
from developTools.message.message_components import Record, Node, Text
from framework_common.framework_util.websocket_fix import ExtendBot
from framework_common.framework_util.yamlLoader import YAMLManager

from run.ai_voice.service.tts import TTS

Tts=TTS()
async def call_tts(bot,event,config,text,speaker=None,mood="中立"):

    # 获取默认模式和 speaker
    mode = config.ai_voice.config["tts"]["tts_engine"]
    speaker = speaker or config.ai_voice.config["tts"][mode]["speaker"]

    # 获取所有 speakers
    all_speakers = (await call_all_speakers(bot, event, config))["speakers"]
    ncspk, acgnspk, modelscope_speakers, vits_speakers, online_vits2_speakers = all_speakers

    # 检查是否有可用 speakers
    if not any(all_speakers):
        bot.logger.error("No speakers found")
        return

    # 定义匹配规则
    '''(acgnspk, [
        (speaker, "acgn_ai"),
        (f"{speaker}【鸣潮】", "acgn_ai"),
        (f"{speaker}【原神】", "acgn_ai"),
        (f"{speaker}【崩坏3】", "acgn_ai"),
        (f"{speaker}【星穹铁道】", "acgn_ai")
    ]),'''  # 已弃用
    speaker_modes = [
        (ncspk, [(speaker, "napcat_tts")]),
        (modelscope_speakers, [(speaker, "modelscope_tts")]),
        (vits_speakers, [(speaker, "vits")]),
        (online_vits2_speakers, [(speaker, "online_vits2")])
    ]

    # 匹配 speaker 和 mode
    for speakers, rules in speaker_modes:
        if not speakers:
            continue
        for spk, new_mode in rules:
            if spk in speakers:
                mode = new_mode
                speaker = speakers[spk] if new_mode == "napcat_tts" else spk
                try:
                    result = await Tts.tts(text=text, speaker=speaker, config=config, mood=mood, bot=bot, mode=mode)
                    await bot.send(event, Record(file=result))
                    return {"status": "success"}
                except Exception:
                    traceback.print_exc()
                    return
    # 如果未匹配，使用默认配置
    try:
        result = await Tts.tts(text=text, speaker=speaker, config=config, mood=mood, bot=bot, mode=mode)
        await bot.send(event, Record(file=result))
        return {"status": "success"}
    except Exception:
        traceback.print_exc()
        return

async def call_all_speakers(bot,event,config):
    return Tts.get_speakers(bot=bot)

def main(bot: ExtendBot,config: YAMLManager):
    @bot.on(GroupMessageEvent)
    async def tts(event: GroupMessageEvent):
        if "说" in event.pure_text and event.pure_text.startswith("/"):
            speaker=event.pure_text.split("说")[0].replace("/","").strip()
            text=event.pure_text.split("说")[1].strip()
            r=await call_tts(bot,event,config,text,speaker)
            if r.get("audio"):
                await bot.send(event, Record(file=r.get("audio")))
        elif event.pure_text=="可用角色":
            #Node(content=[Text("可用角色：")]+[Text(i) for i in get_acgn_ai_speaker_list()])
            all_speakers = await call_all_speakers(bot, event, config)
            all_speakers = all_speakers["speakers"]
            f= all_speakers[0]
            e= all_speakers[1]
            c = all_speakers[2]
            b = all_speakers[3]
            if a:
                a='\n'.join(a)
            if b:
                b='\n'.join(b)
            if f:
                f='\n'.join(f)
            if e:
                e='\n'.join(e)
            if c:
                c='\n'.join(c)
            await bot.send(event, [
                Node(content=[Text(f"使用 /xx说xxxxx")]),
                Node(content=[Text(f"napcat_tts可用角色：\n{f}")]),
                Node(content=[Text(f"modelscope_tts可用角色：\n{c}")]),
                Node(content=[Text(f"vits可用角色：\n{b}")]),
                Node(content=[Text(f"online_vits2可用角色：\n{a}")])])