import zipfile
import os
from typing import Union, List
import re

def sanitize_filename(name: str, replacement: str = "_") -> str:
    # 替换所有非法字符
    return re.sub(r'[\\/:"*?<>|]', replacement, name)
def compress_files(sources: Union[str, List[str]], output_dir: str, zip_name: str = "archive.zip"):
    """
    压缩文件或文件夹，支持单个路径或路径列表。

    :param sources: 文件/文件夹路径或其列表
    :param output_dir: 压缩文件保存的目录
    :param zip_name: 压缩文件的名称（默认 archive.zip）
    """
    zip_name = sanitize_filename(zip_name)
    if isinstance(sources, str):
        sources = [sources]

    os.makedirs(output_dir, exist_ok=True)
    output_zip = os.path.join(output_dir, zip_name)

    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for source in sources:
            if os.path.isfile(source):
                zipf.write(source, os.path.basename(source))
            elif os.path.isdir(source):
                for root, _, files in os.walk(source):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, os.path.dirname(source))
                        zipf.write(file_path, arcname)
            else:
                print(f"跳过无效路径：{source}")

    print(f"压缩完成，文件保存在：{output_zip}")

