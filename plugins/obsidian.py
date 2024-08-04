import os
import re
import asyncio
import aiofiles
import markdown
import imgkit
from concurrent.futures import ThreadPoolExecutor

async def search_markdown_file(directory, folder_pattern, filename_pattern):
    folder_regex = re.compile(folder_pattern, re.IGNORECASE)
    file_regex = re.compile(filename_pattern, re.IGNORECASE)
    matched_files = []

    for root, dirs, files in os.walk(directory):
        if folder_regex.search(root):
            for file in files:
                if file_regex.search(file):
                    matched_files.append(os.path.join(root, file))
    return matched_files

async def read_markdown_file(file_path):
    async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
        return await file.read()

def render_html_to_png(html_content, output_path, config):
    imgkit.from_string(html_content, output_path, config=config)

async def render_markdown_to_png(markdown_content, output_path):
    html_content = markdown.markdown(markdown_content, extensions=['extra', 'codehilite', 'toc'])
    config = imgkit.config(wkhtmltoimage=r'D:\Program Files\wkhtmltopdf\bin\wkhtmltoimage.exe')  # 修改为你的实际路径

    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, render_html_to_png, html_content, output_path, config)

async def main(obsidian_folder, folder_pattern, filename_pattern, output_path):
    matched_files = await search_markdown_file(obsidian_folder, folder_pattern, filename_pattern)
    if matched_files:
        for file_path in matched_files:
            print(f'Found file: {file_path}')
            markdown_content = await read_markdown_file(file_path)
            await render_markdown_to_png(markdown_content, output_path)
            print(f'Rendered image saved to: {output_path}')
    else:
        print('No files found')

# Replace these paths with your actual paths
obsidian_folder = r'D:\gaytub\gdMirror\repo'
folder_pattern = r'.*政治.*'  # Modify this pattern to match your folder structure
filename_pattern = r'5\.0国家.*\.md'  # Modify this pattern to match your file name
output_path = './image.png'

# Run the main function
asyncio.run(main(obsidian_folder, folder_pattern, filename_pattern, output_path))
