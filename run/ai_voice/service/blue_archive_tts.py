import json

import asyncio
import httpx

import importlib.util
import os
import sys

from developTools.utils.logger import get_logger

import ssl
import websockets

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.check_hostname = False  # 关闭主机名检查
ssl_context.verify_mode = ssl.CERT_NONE  # 关闭证书验证



from run.ai_voice.service.online_vits import random_session_hash

logger=get_logger()
async def huggingface_blue_archive_tts(text, speaker,lang_type="ja",proxy=None):
    logger.info(f"params: speaker={speaker}, text={text}, lang_type={lang_type}")
    url = "wss://ori-muchim-bluearchivetts.hf.space/queue/join"
    session_hash = random_session_hash(11)

    async with websockets.connect(url,ssl=ssl_context) as ws:
        logger.info(f"连接到 {url}")
        while True:
            await asyncio.sleep(1)
            result = await ws.recv()
            if result:
                result = json.loads(result)
                print(result)

                if result["msg"] == "send_hash":
                    await ws.send(json.dumps({"session_hash": session_hash, "fn_index": 0}))

                elif result["msg"] == "send_data":
                    await ws.send(json.dumps({
                        "fn_index": 0,
                        "data": [text, speaker, 1.2],
                        "session_hash": session_hash
                    }))

                elif "output" in result:
                    file_url = f"https://ori-muchim-bluearchivetts.hf.space/file={result['output']['data'][1]['name']}"
                    async with httpx.AsyncClient() as client:
                        response = await client.get(file_url)
                        with open(f"data/voice/cache/{session_hash}.wav", "wb") as f:
                            f.write(response.content)
                    return f"data/voice/cache/{session_hash}.wav"
async def get_huggingface_blue_archive_speakers():
    return  ['JP_Airi', 'JP_Akane', 'JP_Akari', 'JP_Ako', 'JP_Aris', 'JP_Arona', 'JP_Aru', 'JP_Asuna', 'JP_Atsuko', 'JP_Ayane', 'JP_Azusa', 'JP_Cherino', 'JP_Chihiro', 'JP_Chinatsu', 'JP_Chise', 'JP_Eimi', 'JP_Erica', 'JP_Fubuki', 'JP_Fuuka', 'JP_Hanae', 'JP_Hanako', 'JP_Hare', 'JP_Haruka', 'JP_Haruna', 'JP_Hasumi', 'JP_Hibiki', 'JP_Hihumi', 'JP_Himari', 'JP_Hina', 'JP_Hinata', 'JP_Hiyori', 'JP_Hoshino', 'JP_Iori', 'JP_Iroha', 'JP_Izumi', 'JP_Izuna', 'JP_Juri', 'JP_Kaede', 'JP_Karin', 'JP_Kayoko', 'JP_Kazusa', 'JP_Kirino', 'JP_Koharu', 'JP_Kokona', 'JP_Kotama', 'JP_Kotori', 'JP_Main', 'JP_Maki', 'JP_Mari', 'JP_Marina', 'JP_Mashiro', 'JP_Michiru', 'JP_Midori', 'JP_Miku', 'JP_Mimori', 'JP_Misaki', 'JP_Miyako', 'JP_Miyu', 'JP_Moe', 'JP_Momoi', 'JP_Momoka', 'JP_Mutsuki', 'JP_NP0013', 'JP_Natsu', 'JP_Neru', 'JP_Noa', 'JP_Nodoka', 'JP_Nonomi', 'JP_Pina', 'JP_Rin', 'JP_Saki', 'JP_Saori', 'JP_Saya', 'JP_Sena', 'JP_Serika', 'JP_Serina', 'JP_Shigure', 'JP_Shimiko', 'JP_Shiroko', 'JP_Shizuko', 'JP_Shun', 'JP_ShunBaby', 'JP_Sora', 'JP_Sumire', 'JP_Suzumi', 'JP_Tomoe', 'JP_Tsubaki', 'JP_Tsurugi', 'JP_Ui', 'JP_Utaha', 'JP_Wakamo', 'JP_Yoshimi', 'JP_Yuuka', 'JP_Yuzu', 'JP_Zunko']

