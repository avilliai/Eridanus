import httpx

from framework_common.utils.random_str import random_str

datap = {"speaker":"宫子（泳装）","text":"上午好"}

modelscopeCookie="cna=j117HdPDmkoCAXjC3hh/4rjk; ajs_anonymous_id=5aa505b4-8510-47b5-a1e3-6ead158f3375; t=27c49d517b916cf11d961fa3769794dd; uuid_tt_dd=11_99759509594-1710000225471-034528; log_Id_click=16; log_Id_pv=12; log_Id_view=277; xlly_s=1; csrf_session=MTcxMzgzODI5OHxEdi1CQkFFQ180SUFBUkFCRUFBQU12LUNBQUVHYzNSeWFXNW5EQW9BQ0dOemNtWlRZV3gwQm5OMGNtbHVad3dTQUJCNFkwRTFkbXAwV0VVME0wOUliakZwfHNEIp5sKWkjeJWKw1IphSS3e4R_7GyEFoKKuDQuivUs; csrf_token=TkLyvVj3to4G5Mn_chtw3OI8rRA%3D; _samesite_flag_=true; cookie2=11ccab40999fa9943d4003d08b6167a0; _tb_token_=555ee71fdee17; _gid=GA1.2.1037864555.1713838369; h_uid=2215351576043; _xsrf=2|f9186bd2|74ae7c9a48110f4a37f600b090d68deb|1713840596; csg=242c1dff; m_session_id=769d7c25-d715-4e3f-80de-02b9dbfef325; _gat_gtag_UA_156449732_1=1; _ga_R1FN4KJKJH=GS1.1.1713838368.22.1.1713841094.0.0.0; _ga=GA1.1.884310199.1697973032; tfstk=fE4KxBD09OXHPxSuRWsgUB8pSH5GXivUTzyBrU0oKGwtCSJHK7N3ebe0Ce4n-4Y8X8wideDotbQ8C7kBE3queYwEQ6OotW08WzexZUVIaNlgVbmIN7MQBYNmR0rnEvD-y7yAstbcoWPEz26cnZfu0a_qzY_oPpRUGhg5ntbgh_D3W4ZudTQmX5MZwX9IN8ts1AlkAYwSdc9sMjuSF8g56fGrgX9SFbgs5bGWtBHkOYL8Srdy07KF-tW4Wf6rhWQBrfUt9DHbOyLWPBhKvxNIBtEfyXi_a0UyaUn8OoyrGJ9CeYzT1yZbhOxndoh8iuFCRFg38WZjVr6yVWunpVaQDQT762H3ezewpOHb85aq5cbfM5aaKWzTZQ_Ss-D_TygRlsuKRvgt_zXwRYE_VymEzp6-UPF_RuIrsr4vHFpmHbxC61Ky4DGguGhnEBxD7Zhtn1xM43oi_fHc61Ky4DGZ6xfGo3-rjf5..; isg=BKKjOsZlMNqsZy8UH4-lXjE_8ygE86YNIkwdKew665XKv0I51IGvHCUz7_tDrx6l"

async def modelscope_tts(text, speaker):

    if text == "" or text == " ":
        text = "哼哼"

    headers = {
        "Content-Type": "application/json",
        "Origin": "https://www.modelscope.cn",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
        "Cookie": modelscopeCookie
    }
    if text == "" or text == " ":
        text = "哼哼"
    if speaker == "阿梓":
        url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Azusa-Bert-VITS2-2.3/gradio/run/predict"
        newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/Azusa-Bert-VITS2-2.3/gradio/file="
    elif speaker == "BT":
        speaker = "Speaker"
        url = "https://www.modelscope.cn/api/v1/studio/MiDd1Eye/BT7274-Bert-VITS2/gradio/run/predict"
        newurp = "https://www.modelscope.cn/api/v1/studio/MiDd1Eye/BT7274-Bert-VITS2/gradio/file="
    elif speaker == "otto":
        url = "https://www.modelscope.cn/api/v1/studio/xzjosh/otto-Bert-VITS2-2.3/gradio/run/predict"
        newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/otto-Bert-VITS2-2.3/gradio/file="
    elif speaker == "塔菲":
        speaker = "taffy"
        url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Taffy-Bert-VITS2/gradio/run/predict"
        newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/Taffy-Bert-VITS2/gradio/file="
    elif speaker == "星瞳":
        speaker = "XingTong"
        url = "https://www.modelscope.cn/api/v1/studio/xzjosh/XingTong-Bert-VITS2/gradio/run/predict"
        newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/XingTong-Bert-VITS2/gradio/file="
    elif speaker == "丁真":
        url = "https://s5k.cn/api/v1/studio/MiDd1Eye/DZ-Bert-VITS2/gradio/run/predict"
        newurp = "https://s5k.cn/api/v1/studio/MiDd1Eye/DZ-Bert-VITS2/gradio/file="
        speaker = "Speaker"
    elif speaker == "东雪莲":
        url = "https://xzjosh-azuma-bert-vits2-2-3.ms.show/run/predict"
        newurp = "https://xzjosh-azuma-bert-vits2-2-3.ms.show/file="
    elif speaker == "嘉然":
        url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Diana-Bert-VITS2-2.3/gradio/run/predict"
        newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/Diana-Bert-VITS2-2.3/gradio/file="
    elif speaker == "孙笑川":
        url = "https://www.modelscope.cn/api/v1/studio/xzjosh/SXC-Bert-VITS2/gradio/run/predict"
        newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/SXC-Bert-VITS2/gradio/file="
    elif speaker == "鹿鸣":
        speaker = "Lumi"
        url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Lumi-Bert-VITS2/gradio/run/predict"
        newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/Lumi-Bert-VITS2/gradio/file="
    elif speaker == "文静":
        speaker = "Wenjing"
        url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Wenjing-Bert-VITS2/gradio/run/predict"
        newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/Wenjing-Bert-VITS2/gradio/file="
    elif speaker == "亚托克斯":
        speaker = "Aatrox"
        url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Aatrox-Bert-VITS2/gradio/run/predict"
        newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/Aatrox-Bert-VITS2/gradio/file="
    elif speaker == "奶绿":
        speaker = "明前奶绿"
        url = "https://www.modelscope.cn/api/v1/studio/xzjosh/LAPLACE-Bert-VITS2-2.3/gradio/run/predict"
        newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/LAPLACE-Bert-VITS2-2.3/gradio/file="
    elif speaker == "七海":
        speaker = "Nana7mi"
        url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Nana7mi-Bert-VITS2/gradio/run/predict"
        newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/Nana7mi-Bert-VITS2/gradio/file="
    elif speaker == "恬豆":
        speaker = "Bekki"
        url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Bekki-Bert-VITS2/gradio/run/predict"
        newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/Bekki-Bert-VITS2/gradio/file="
    elif speaker == "科比":
        url = "https://www.modelscope.cn/api/v1/studio/xzjosh/Kobe-Bert-VITS2-2.3/gradio/run/predict"
        newurp = "https://www.modelscope.cn/api/v1/studio/xzjosh/Kobe-Bert-VITS2-2.3/gradio/file="
    elif speaker == "胡桃":
        speaker = "hutao"
        url = "https://www.modelscope.cn/api/v1/studio/Xzkong/AI-hutao/gradio/run/predict"
        newurp = "https://www.modelscope.cn/api/v1/studio/Xzkong/AI-hutao/gradio/file="
    data = {
        "data": [text, speaker, 0.5, 0.5, 0.9, 1, "auto", None, "Happy", "Text prompt", "", 0.7],
        "event_data": None,
        "fn_index": 0,
        "dataType": ["textbox", "dropdown", "slider", "slider", "slider", "slider", "dropdown", "audio", "textbox",
                     "radio", "textbox", "slider"],
        "session_hash": "xjwen214wqf"
    }
    p = f"data/voice/cache/{random_str()}.wav"
    async with httpx.AsyncClient(timeout=200, headers=headers) as client:
        r = await client.post(url, json=data)
        newurl = newurp + \
                 r.json().get("data")[1].get("name")
        async with httpx.AsyncClient(timeout=200, headers=headers) as client:
            r = await client.get(newurl)
            with open(p, "wb") as f:
                f.write(r.content)
            return p
def get_modelscope_tts_speakers():
    return ["阿梓", "BT", "otto", "塔菲", "星瞳", "丁真", "东雪莲", "嘉然", "孙笑川", "鹿鸣", "文静", "亚托克斯", "奶绿", "七海", "恬豆", "科比"]