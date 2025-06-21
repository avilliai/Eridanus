import html
import re
from typing import Dict, Union, Generator


# 定义通用解析 CQ 码的函数
def parse_message_with_cq_codes_to_list(message: str) -> Generator[Dict[str, Union[str, Dict]]]:
    cq_pattern = r'\[CQ:(\w+),(.*?)\]'
    parsed_result = []
    last_end = 0

    for match in re.finditer(cq_pattern, message):
        start, end = match.span()
        cq_type = match.group(1)
        cq_params = match.group(2)
        params = dict(param.split('=', 1) for param in cq_params.split(',') if '=' in param)


        for key, value in params.items():
            params[key] = unescape_cq_value(value)

        if start > last_end:
            parsed_result.append({
                "type": "text",
                "text": unescape_cq_value(message[last_end:start])
            })

        params["type"] = cq_type

        parsed_result.append(params)
        last_end = end

    if last_end < len(message):
        parsed_result.append({
            "type": "text",
            "text": unescape_cq_value(message[last_end:])
        })

    for item in parsed_result:
        if item['type'] == "text":
            yield {"text": item["text"]}
        else:
            cq_type = item['type']
            yield {cq_type: item}

def unescape_cq_value(text: str) -> str:
    """反转义 CQ 码中的 &, [, ] 和 ,"""
    text = text.replace("[", "[")
    text = text.replace("]", "]")
    text = text.replace(",", ",")
    return html.unescape(text)

def parse_message_2processed_message(message: dict) -> Generator[Dict[str, Union[str, Dict]]]:
    for item in message:
        if item["type"] == "text":
            yield {"text": item["data"]["text"]}
        else:
            yield {item["type"]: item["data"]}