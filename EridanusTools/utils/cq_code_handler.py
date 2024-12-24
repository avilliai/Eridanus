import re
from typing import List, Dict, Union


# 定义通用解析 CQ 码的函数
def parse_message_with_cq_codes_to_list(message: str) -> List[Dict[str, Union[str, Dict]]]:
    # 定义正则表达式匹配 CQ 码
    cq_pattern = r'\[CQ:(\w+),(.*?)\]'
    parsed_result = []
    last_end = 0

    for match in re.finditer(cq_pattern, message):
        start, end = match.span()
        cq_type = match.group(1)
        cq_params = match.group(2)

        # 提取 CQ 码参数
        params = dict(param.split('=', 1) for param in cq_params.split(',') if '=' in param)

        # 如果 CQ 码前有普通文本，将其添加到结果
        if start > last_end:
            parsed_result.append({
                "type": "text",
                "text": message[last_end:start]
            })

        # 根据 CQ 类型处理
        params["type"] = cq_type  # 动态添加 type 字段，以保持通用性

        # 添加解析后的 CQ 码
        parsed_result.append(params)
        last_end = end

    # 添加最后一段普通文本
    if last_end < len(message):
        parsed_result.append({
            "type": "text",
            "text": message[last_end:]
        })

    # 组装最终的结果结构
    result = []
    for item in parsed_result:
        if item['type'] == "text":
            result.append({"text": item["text"]})
        else:
            # 对于每个 CQ 码，根据 type 动态添加
            cq_type = item['type']
            result.append({cq_type: item})

    return result



