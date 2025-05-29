import json
import os

def json_check(json_img):
    if not isinstance(json_img, list):
        raise ValueError("input must be a list")

    json_check_reload=[]
    for per_json_check in json_check:
        if isinstance(per_json_check, dict):
            if 'type' in per_json_check and per_json_check['type'] in ['avatar','img','text']:
                if 'subtype' not in per_json_check:
                    per_json_check['subtype']='common'

            elif 'type' not in per_json_check and isinstance(per_json_check, str) :

                per_json_check={'type':'text','subtype':'common','content':per_json_check[0]}

                per_json_check_img=[]
                for per_json_check_per in per_json_check:
                    if os.path.splitext(per_json_check_per)[1].lower() in [".jpg", ".png", ".jpeg", '.webp'] or per_json_check_per.startswith("http"):
                        per_json_check_img.append(per_json_check_per)


                if per_json_check_img != []:
                    per_json_check = {'type': 'img', 'subtype': 'common', 'img': per_json_check_img}
                elif per_json_check_img == []:
                    per_json_check = {'type': 'text', 'subtype': 'common', 'content': per_json_check[0]}
            json_check_reload.append(per_json_check)
        elif isinstance(per_json_check, set):





def json_check_test():
    json_check={'nihaodaf'}
    for per_json_check in json_check:
        print(per_json_check)
    print(json_check[0])

if __name__ == '__main__':
    json_check_test()