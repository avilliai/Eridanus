import os
import time
import asyncio

from developTools.utils.logger import get_logger

logger=get_logger()
async def delete_old_files_async(folder_path):
    """
    异步删除文件夹中过期的文件
    :param folder_path:
    :return:
    """
    current_time = time.time()
    time_threshold = 3600

    deleted_file_sizes = []

    async def process_file(file_path):
        nonlocal deleted_file_sizes
        try:
            if file_path.endswith(".py") or file_path.endswith(".ttf"):
                #print(f"跳过文件: {file_path}")
                return

            file_mtime = os.path.getmtime(file_path)

            if current_time - file_mtime > time_threshold:
                file_size = os.path.getsize(file_path) / (1024 * 1024)
                deleted_file_sizes.append(file_size)
                await asyncio.to_thread(os.remove, file_path)
                #print(f"已删除文件: {file_path} (大小: {file_size:.2f} MB)")
        except Exception as e:
            logger.error(f"处理文件失败: {file_path} - {e}")

    # 获取所有文件路径
    tasks = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # 检查是否是文件（跳过文件夹）
        if os.path.isfile(file_path):
            tasks.append(process_file(file_path))

    # 等待所有文件处理任务完成
    await asyncio.gather(*tasks)

    # 统计删除的文件总大小
    total_deleted_size = sum(deleted_file_sizes)
    return total_deleted_size