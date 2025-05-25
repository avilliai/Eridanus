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



def install_and_import(package_name):
    """检测模块是否已安装，若未安装则通过 pip 安装"""
    # 检查模块是否已经安装
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        print(f"{package_name} 未安装，正在安装...")
        # 使用 os.system 安装模块
        os.system(f"{sys.executable} -m pip install {package_name}")
        # 安装后再次导入模块
        spec = importlib.util.find_spec(package_name)
        if spec is None:
            print(f"安装失败：无法找到 {package_name} 模块")
            return None
    return importlib.import_module(package_name)



from run.ai_voice.service.online_vits import random_session_hash

logger=get_logger()
async def huggingface_online_vits2(text, speaker,lang_type="简体中文",proxy=None):
    logger.info(f"params: speaker={speaker}, text={text}, lang_type={lang_type}")
    url = "wss://plachta-vits-umamusume-voice-synthesizer.hf.space/queue/join"
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
                    await ws.send(json.dumps({"session_hash": session_hash, "fn_index": 2}))

                elif result["msg"] == "send_data":
                    await ws.send(json.dumps({
                        "fn_index": 2,
                        "data": [text, speaker, lang_type, 1, False],
                        "session_hash": session_hash
                    }))

                elif "output" in result:
                    file_url = f"https://plachta-vits-umamusume-voice-synthesizer.hf.space/file={result['output']['data'][1]['name']}"
                    async with httpx.AsyncClient() as client:
                        response = await client.get(file_url)
                        with open(f"data/voice/cache/{session_hash}.wav", "wb") as f:
                            f.write(response.content)
                    return f"data/voice/cache/{session_hash}.wav"
async def get_huggingface_online_vits2_speakers():
    return   list({"特别周 Special Week (Umamusume Pretty Derby)": 0,
    "无声铃鹿 Silence Suzuka (Umamusume Pretty Derby)": 1,
    "东海帝王 Tokai Teio (Umamusume Pretty Derby)": 2,
    "丸善斯基 Maruzensky (Umamusume Pretty Derby)": 3,
    "富士奇迹 Fuji Kiseki (Umamusume Pretty Derby)": 4,
    "小栗帽 Oguri Cap (Umamusume Pretty Derby)": 5,
    "黄金船 Gold Ship (Umamusume Pretty Derby)": 6,
    "伏特加 Vodka (Umamusume Pretty Derby)": 7,
    "大和赤骥 Daiwa Scarlet (Umamusume Pretty Derby)": 8,
    "大树快车 Taiki Shuttle (Umamusume Pretty Derby)": 9,
    "草上飞 Grass Wonder (Umamusume Pretty Derby)": 10,
    "菱亚马逊 Hishi Amazon (Umamusume Pretty Derby)": 11,
    "目白麦昆 Mejiro Mcqueen (Umamusume Pretty Derby)": 12,
    "神鹰 El Condor Pasa (Umamusume Pretty Derby)": 13,
    "好歌剧 T.M. Opera O (Umamusume Pretty Derby)": 14,
    "成田白仁 Narita Brian (Umamusume Pretty Derby)": 15,
    "鲁道夫象征 Symboli Rudolf (Umamusume Pretty Derby)": 16,
    "气槽 Air Groove (Umamusume Pretty Derby)": 17,
    "爱丽数码 Agnes Digital (Umamusume Pretty Derby)": 18,
    "青云天空 Seiun Sky (Umamusume Pretty Derby)": 19,
    "玉藻十字 Tamamo Cross (Umamusume Pretty Derby)": 20,
    "美妙姿势 Fine Motion (Umamusume Pretty Derby)": 21,
    "琵琶晨光 Biwa Hayahide (Umamusume Pretty Derby)": 22,
    "重炮 Mayano Topgun (Umamusume Pretty Derby)": 23,
    "曼城茶座 Manhattan Cafe (Umamusume Pretty Derby)": 24,
    "美普波旁 Mihono Bourbon (Umamusume Pretty Derby)": 25,
    "目白雷恩 Mejiro Ryan (Umamusume Pretty Derby)": 26,
    "雪之美人 Yukino Bijin (Umamusume Pretty Derby)": 28,
    "米浴 Rice Shower (Umamusume Pretty Derby)": 29,
    "艾尼斯风神 Ines Fujin (Umamusume Pretty Derby)": 30,
    "爱丽速子 Agnes Tachyon (Umamusume Pretty Derby)": 31,
    "爱慕织姬 Admire Vega (Umamusume Pretty Derby)": 32,
    "稻荷一 Inari One (Umamusume Pretty Derby)": 33,
    "胜利奖券 Winning Ticket (Umamusume Pretty Derby)": 34,
    "空中神宫 Air Shakur (Umamusume Pretty Derby)": 35,
    "荣进闪耀 Eishin Flash (Umamusume Pretty Derby)": 36,
    "真机伶 Curren Chan (Umamusume Pretty Derby)": 37,
    "川上公主 Kawakami Princess (Umamusume Pretty Derby)": 38,
    "黄金城市 Gold City (Umamusume Pretty Derby)": 39,
    "樱花进王 Sakura Bakushin O (Umamusume Pretty Derby)": 40,
    "采珠 Seeking the Pearl (Umamusume Pretty Derby)": 41,
    "新光风 Shinko Windy (Umamusume Pretty Derby)": 42,
    "东商变革 Sweep Tosho (Umamusume Pretty Derby)": 43,
    "超级小溪 Super Creek (Umamusume Pretty Derby)": 44,
    "醒目飞鹰 Smart Falcon (Umamusume Pretty Derby)": 45,
    "荒漠英雄 Zenno Rob Roy (Umamusume Pretty Derby)": 46,
    "东瀛佐敦 Tosen Jordan (Umamusume Pretty Derby)": 47,
    "中山庆典 Nakayama Festa (Umamusume Pretty Derby)": 48,
    "成田大进 Narita Taishin (Umamusume Pretty Derby)": 49,
    "西野花 Nishino Flower (Umamusume Pretty Derby)": 50,
    "春乌拉拉 Haru Urara (Umamusume Pretty Derby)": 51,
    "青竹回忆 Bamboo Memory (Umamusume Pretty Derby)": 52,
    "待兼福来 Matikane Fukukitaru (Umamusume Pretty Derby)": 55,
    "名将怒涛 Meisho Doto (Umamusume Pretty Derby)": 57,
    "目白多伯 Mejiro Dober (Umamusume Pretty Derby)": 58,
    "优秀素质 Nice Nature (Umamusume Pretty Derby)": 59,
    "帝王光环 King Halo (Umamusume Pretty Derby)": 60,
    "待兼诗歌剧 Matikane Tannhauser (Umamusume Pretty Derby)": 61,
    "生野狄杜斯 Ikuno Dictus (Umamusume Pretty Derby)": 62,
    "目白善信 Mejiro Palmer (Umamusume Pretty Derby)": 63,
    "大拓太阳神 Daitaku Helios (Umamusume Pretty Derby)": 64,
    "双涡轮 Twin Turbo (Umamusume Pretty Derby)": 65,
    "里见光钻 Satono Diamond (Umamusume Pretty Derby)": 66,
    "北部玄驹 Kitasan Black (Umamusume Pretty Derby)": 67,
    "樱花千代王 Sakura Chiyono O (Umamusume Pretty Derby)": 68,
    "天狼星象征 Sirius Symboli (Umamusume Pretty Derby)": 69,
    "目白阿尔丹 Mejiro Ardan (Umamusume Pretty Derby)": 70,
    "八重无敌 Yaeno Muteki (Umamusume Pretty Derby)": 71,
    "鹤丸刚志 Tsurumaru Tsuyoshi (Umamusume Pretty Derby)": 72,
    "目白光明 Mejiro Bright (Umamusume Pretty Derby)": 73,
    "樱花桂冠 Sakura Laurel (Umamusume Pretty Derby)": 74,
    "成田路 Narita Top Road (Umamusume Pretty Derby)": 75,
    "也文摄辉 Yamanin Zephyr (Umamusume Pretty Derby)": 76,
    "真弓快车 Aston Machan (Umamusume Pretty Derby)": 80,
    "骏川手纲 Hayakawa Tazuna (Umamusume Pretty Derby)": 81,
    "小林历奇 Kopano Rickey (Umamusume Pretty Derby)": 83,
    "奇锐骏 Wonder Acute (Umamusume Pretty Derby)": 85,
    "秋川理事长 President Akikawa (Umamusume Pretty Derby)": 86,
    "綾地 寧々 Ayachi Nene (Sanoba Witch)": 87,
    "因幡 めぐる Inaba Meguru (Sanoba Witch)": 88,
    "椎葉 紬 Shiiba Tsumugi (Sanoba Witch)": 89,
    "仮屋 和奏 Kariya Wakama (Sanoba Witch)": 90,
    "戸隠 憧子 Togakushi Touko (Sanoba Witch)": 91,
    "九条裟罗 Kujou Sara (Genshin Impact)": 92,
    "芭芭拉 Barbara (Genshin Impact)": 93,
    "派蒙 Paimon (Genshin Impact)": 94,
    "荒泷一斗 Arataki Itto (Genshin Impact)": 96,
    "早柚 Sayu (Genshin Impact)": 97,
    "香菱 Xiangling (Genshin Impact)": 98,
    "神里绫华 Kamisato Ayaka (Genshin Impact)": 99,
    "重云 Chongyun (Genshin Impact)": 100,
    "流浪者 Wanderer (Genshin Impact)": 102,
    "优菈 Eula (Genshin Impact)": 103,
    "凝光 Ningguang (Genshin Impact)": 105,
    "钟离 Zhongli (Genshin Impact)": 106,
    "雷电将军 Raiden Shogun (Genshin Impact)": 107,
    "枫原万叶 Kaedehara Kazuha (Genshin Impact)": 108,
    "赛诺 Cyno (Genshin Impact)": 109,
    "诺艾尔 Noelle (Genshin Impact)": 112,
    "八重神子 Yae Miko (Genshin Impact)": 113,
    "凯亚 Kaeya (Genshin Impact)": 114,
    "魈 Xiao (Genshin Impact)": 115,
    "托马 Thoma (Genshin Impact)": 116,
    "可莉 Klee (Genshin Impact)": 117,
    "迪卢克 Diluc (Genshin Impact)": 120,
    "夜兰 Yelan (Genshin Impact)": 121,
    "鹿野院平藏 Shikanoin Heizou (Genshin Impact)": 123,
    "辛焱 Xinyan (Genshin Impact)": 124,
    "丽莎 Lisa (Genshin Impact)": 125,
    "云堇 Yun Jin (Genshin Impact)": 126,
    "坎蒂丝 Candace (Genshin Impact)": 127,
    "罗莎莉亚 Rosaria (Genshin Impact)": 128,
    "北斗 Beidou (Genshin Impact)": 129,
    "珊瑚宫心海 Sangonomiya Kokomi (Genshin Impact)": 132,
    "烟绯 Yanfei (Genshin Impact)": 133,
    "久岐忍 Kuki Shinobu (Genshin Impact)": 136,
    "宵宫 Yoimiya (Genshin Impact)": 139,
    "安柏 Amber (Genshin Impact)": 143,
    "迪奥娜 Diona (Genshin Impact)": 144,
    "班尼特 Bennett (Genshin Impact)": 146,
    "雷泽 Razor (Genshin Impact)": 147,
    "阿贝多 Albedo (Genshin Impact)": 151,
    "温迪 Venti (Genshin Impact)": 152,
    "空 Player Male (Genshin Impact)": 153,
    "神里绫人 Kamisato Ayato (Genshin Impact)": 154,
    "琴 Jean (Genshin Impact)": 155,
    "艾尔海森 Alhaitham (Genshin Impact)": 156,
    "莫娜 Mona (Genshin Impact)": 157,
    "妮露 Nilou (Genshin Impact)": 159,
    "胡桃 Hu Tao (Genshin Impact)": 160,
    "甘雨 Ganyu (Genshin Impact)": 161,
    "纳西妲 Nahida (Genshin Impact)": 162,
    "刻晴 Keqing (Genshin Impact)": 165,
    "荧 Player Female (Genshin Impact)": 169,
    "埃洛伊 Aloy (Genshin Impact)": 179,
    "柯莱 Collei (Genshin Impact)": 182,
    "多莉 Dori (Genshin Impact)": 184,
    "提纳里 Tighnari (Genshin Impact)": 186,
    "砂糖 Sucrose (Genshin Impact)": 188,
    "行秋 Xingqiu (Genshin Impact)": 190,
    "奥兹 Oz (Genshin Impact)": 193,
    "五郎 Gorou (Genshin Impact)": 198,
    "达达利亚 Tartalia (Genshin Impact)": 202,
    "七七 Qiqi (Genshin Impact)": 207,
    "申鹤 Shenhe (Genshin Impact)": 217,
    "莱依拉 Layla (Genshin Impact)": 228,
    "菲谢尔 Fishl (Genshin Impact)": 230
  }.keys())