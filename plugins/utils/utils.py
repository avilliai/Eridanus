import random
import httpx

def random_str(random_length=7, chars='AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'):
    """
    生成随机字符串作为验证码
    :param random_length: 字符串长度,默认为6
    :return: 随机字符串
    """
    string = ''

    length = len(chars) - 1
    # random = Random()
    # 设置循环每次取一个字符用来生成随机数
    for i in range(random_length):
        string += (chars[random.randint(0, length)])
    return string

async def url_to_base64(url):
    async with httpx.AsyncClient(timeout=9000) as client:
        response = await client.get(url)
        if response.status_code == 200:
            image_bytes = response.content
            encoded_string = base64.b64encode(image_bytes).decode('utf-8')
            return encoded_string
        else:
            raise Exception(f"Failed to retrieve image: {response.status_code}")

def parse_arguments(arg_string):
    args = arg_string.split()
    print(f"Split arguments: {args}")  # 调试信息
    result = {}
    for arg in args:
        if arg.startswith('-') and len(arg) > 1:
            # 找到第一个数字的位置
            for i, char in enumerate(arg[1:], start=1):
                if char.isdigit():
                    break
            else:
                continue
            
            key = arg[1:i]
            value = arg[i:]
            try:
                value = int(value)
            except ValueError:
                print(f"Warning: Invalid value for key '{key}'")  # 调试信息
                continue
            result[key] = value
        else:
            print(f"Warning: Invalid argument format '{arg}'")  # 调试信息
    return result
