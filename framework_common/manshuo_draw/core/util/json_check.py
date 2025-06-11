import json
import os

def json_check(json_img):
    if not isinstance(json_img, list):
        raise ValueError("input must be a list")

    json_check_reload=[]
    for per_json_check in json_img:
        if isinstance(per_json_check, dict):#判断是否为正确格式（字典）若是，则检查其中参数是否完整
            if 'type' in per_json_check and per_json_check['type'] in ['avatar','img','text','games']:#判断是否有一级分类
                if 'subtype' not in per_json_check:#判断是否有二级分类，若没有，统一分给common类
                    per_json_check['subtype']='common'
                json_check_reload.append(per_json_check)
            elif 'type' in per_json_check and per_json_check['type'] in ['basic_set','backdrop']:#判断是否有基础设置
                json_check_reload.append(per_json_check)
            else:
                continue
        elif isinstance(per_json_check, set) or isinstance(per_json_check, list):
            collect_img,collect_text=[],[]
            for per_json_check_per in per_json_check:
                if os.path.splitext(per_json_check_per)[1].lower() in [".jpg", ".png", ".jpeg", '.webp'] or per_json_check_per.startswith("http"):
                    collect_img.append(per_json_check_per)
                else:
                    collect_text.append(per_json_check_per)
            if collect_img:
                json_check_reload.append({'type':'img','subtype':'common','img':collect_img})
            if collect_text:
                json_check_reload.append({'type':'text','subtype':'common','content':collect_text})
        else:
            collect_img,collect_text=[],[]
            if isinstance(per_json_check, str) and (os.path.splitext(per_json_check)[1].lower() in [".jpg", ".png", ".jpeg",'.webp'] or per_json_check.startswith("http")):
                collect_img.append(per_json_check)
            else:
                collect_text.append(f'{per_json_check}')
            if collect_img:
                json_check_reload.append({'type':'img','subtype':'common','img':collect_img})
            if collect_text:
                json_check_reload.append({'type':'text','subtype':'common','content':collect_text})

    if  'basic_set' not in [per_json_check['type'] for per_json_check in json_check_reload]:
        json_check_reload.append({'type': 'basic_set'})
    if 'backdrop' not in [per_json_check['type'] for per_json_check in json_check_reload]:
        json_check_reload.append({'type': 'backdrop', 'subtype': 'gradient'})
    return json_check_reload


if __name__ == '__main__':
    pass