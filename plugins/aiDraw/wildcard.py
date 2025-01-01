import os
import random
import re
import aiofiles

async def get_random_lines(file_path, count):
    async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
        lines = [line.strip() async for line in file if line.strip()]
        if not lines:
            raise ValueError(f"No content found in {file_path}")
        return [random.choice(lines) for _ in range(min(count, len(lines)))]

def add_random_float(item):
    n = round(random.uniform(0, 1), 4)
    if n == 1.0:
        return item
    else:
        return f"({item}:{n})"

async def replace_wildcards(input_string, wildcards_relative_path='wildcards'):
    items = input_string.split(',')
    pattern = re.compile(r'<wd:([a-zA-Z0-9_]+)(?:=([0-9]+))?>')
    current_dir = os.path.dirname(os.path.abspath(__file__))
    wildcards_dir = os.path.join(current_dir, wildcards_relative_path)
    if not os.path.isdir(wildcards_dir):
        raise NotADirectoryError(f"The directory does not exist: {wildcards_dir}")
    result_items = []
    replacement_log = ""
    for item in items:
        match = pattern.match(item)
        if match:
            wildcard_name, num_lines_str = match.groups()
            file_path = os.path.join(wildcards_dir, f'{wildcard_name}.txt')
            if not os.path.isfile(file_path):
                result_items.append(item)
                continue
            try:
                if num_lines_str:
                    num_lines = int(num_lines_str)
                    selected_items = await get_random_lines(file_path, num_lines)
                    replaced_items = [add_random_float(x) for x in selected_items]
                    replaced_str = ','.join(replaced_items)
                else:
                    replaced_item = add_random_float(await get_random_lines(file_path, 1)[0])
                    replaced_str = replaced_item
                for rep in replaced_items if num_lines_str else [replaced_item]:
                    result_items.append(rep)
                replacement_log += f"{item} -> {replaced_str};"
            except ValueError:
                raise ValueError(f"Invalid number of lines: {num_lines_str}")
            except Exception as e:
                raise e
        else:
            result_items.append(item)
    result = ','.join(result_items)
    log = replacement_log.rstrip(';') if replacement_log else False
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
        wildcard_strings = [f"<wd:{os.path.splitext(f)[0]}=1>" for f in available_files]
        result_string = '\n'.join(wildcard_strings)
        return result_string
    except Exception as e:
        print("An error occurred while scanning the directory:", e)
        return "无wildcard"