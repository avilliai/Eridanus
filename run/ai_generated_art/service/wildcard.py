import os
import random
import re
import aiofiles
import asyncio

async def get_random_lines(file_path, count):
    async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
        lines = [line.strip() async for line in file if line.strip()]
        if not lines:
            raise ValueError(f"No content found in {file_path}")
        return [random.choice(lines) for _ in range(min(count, len(lines)))]

def add_weight(item, weight_type, a=1.0, b=None):
    if weight_type == 'fixed':
        n = round(a, 4)
    elif weight_type == 'range' and b is not None:
        n = round(random.uniform(a, b), 4)
    else:
        raise ValueError("Invalid weight type or parameters")

    if n == 1.0:
        return item
    else:
        return f"({item}:{n})"

def parse_weight_params(weight_str):
    try:
        if not weight_str:
            warning_msg = "无效的权重参数 ''，使用默认权重 0 到 1."
            print(warning_msg)
            return 'range', 0.0, 1.0, warning_msg

        weight_str = weight_str.replace('wd', '', 1)

        try:
            a = float(weight_str)
            return 'fixed', a, None, None
        except ValueError:
            pass

        if '-' in weight_str:
            a, b = map(float, weight_str.split('-'))
            if a <= b:
                return 'range', a, b, None
            else:
                raise ValueError("Invalid weight range: start must be less than or equal to end.")

        warning_msg = f"无效的权重参数 '{weight_str}'，使用默认权重 0 到 1."
        print(warning_msg)
        return 'range', 0.0, 1.0, warning_msg
    except (ValueError, TypeError) as e:
        warning_msg = f"无效的权重参数 '{weight_str}'，使用默认权重 0 到 1. 错误信息: {e}"
        print(warning_msg)
        return 'range', 0.0, 1.0, warning_msg

async def replace_wildcards(input_string, wildcards_relative_path='wildcards'):
    pattern = re.compile(r'<(wd[^:]*):([^=]+)(?:=([0-9]+))?>', re.UNICODE)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    wildcards_dir = os.path.join(current_dir, wildcards_relative_path)
    if not os.path.isdir(wildcards_dir):
        raise NotADirectoryError(f"The directory does not exist: {wildcards_dir}")

    matches = list(pattern.finditer(input_string))
    replacement_tasks = []

    for match in matches:
        weight_part, wildcard_name, num_lines_str = match.groups()
        file_path = os.path.join(wildcards_dir, f'{wildcard_name}.txt')

        async def process_match(match, weight_part, file_path, num_lines_str=None):
            if not os.path.isfile(file_path):
                return match.group(0), None, None

            try:
                num_lines = int(num_lines_str) if num_lines_str else 1
                weight_type, a, b, log_entry = parse_weight_params(weight_part)

                selected_items = await get_random_lines(file_path, num_lines)

                replaced_items = []
                for item in selected_items:
                    if weight_type == 'fixed':
                        replaced_item = add_weight(item, 'fixed', a=a)
                    elif weight_type == 'range':
                        replaced_item = add_weight(item, 'range', a=a, b=b)
                    else:
                        raise ValueError("Invalid weight type")

                    replaced_items.append(replaced_item)

                replaced_str = ','.join(replaced_items)
                return replaced_str, f"{match.group(0)} -> {replaced_str}", log_entry
            except (ValueError, TypeError) as e:
                error_msg = f"Invalid number of lines or weight parameters: {e}"
                print(error_msg)
                return match.group(0), None, error_msg
            except Exception as e:
                error_msg = f"Unexpected error: {e}"
                print(error_msg)
                return match.group(0), None, error_msg

        replacement_tasks.append(process_match(match, weight_part, file_path, num_lines_str))

    replacements = await asyncio.gather(*replacement_tasks)
    parts = []
    last_end = 0
    replacement_log = []
    for i, match in enumerate(matches):
        parts.append(input_string[last_end:match.start()])
        new_str, log_entry, weight_log = replacements[i]
        if log_entry and weight_log:
            combined_log = f"{log_entry}, {weight_log}"
            replacement_log.append(combined_log)
        elif log_entry:
            replacement_log.append(log_entry)
        elif weight_log:
            replacement_log.append(weight_log)
        parts.append(new_str or match.group(0))
        last_end = match.end()
    parts.append(input_string[last_end:])
    result = ''.join(parts)
    log = '\n'.join(replacement_log) if replacement_log else False
    return result, log

async def get_available_wildcards(wildcards_relative_path='wildcards'):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    wildcards_dir = os.path.join(current_dir, wildcards_relative_path)
    if not os.path.isdir(wildcards_dir):
        return "无wildcard"
    
    try:
        available_files = []
        for entry in os.scandir(wildcards_dir):
            if entry.is_file() and entry.name.endswith('.txt'):
                available_files.append(entry.name)
        if not available_files:
            return "无wildcard"
        wildcard_strings = [f"<wd1:{os.path.splitext(f)[0]}=1>" for f in available_files]
        result_string = '\n'.join(wildcard_strings)
        return result_string
    except Exception as e:
        print("An error occurred while scanning the directory:", e)
        return "无wildcard"
