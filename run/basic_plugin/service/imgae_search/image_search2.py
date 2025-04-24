import asyncio
from typing import Tuple, Optional, List, Dict, Any

from developTools.utils.logger import get_logger
from run.basic_plugin.service.imgae_search.anime_trace import anime_trace

from run.basic_plugin.service.imgae_search.sauceno_api import saucenao

logger=get_logger()
async def fetch_results(proxies, url: str,sauceno_api:str) -> Dict[str, Optional[List[Any]]]:
    if proxies=="":
        proxies=None

    async def _safe_call(func, *args, **kwargs) -> Tuple[str, Optional[List[Any]]]:
        try:
            result = await asyncio.wait_for(func(*args, **kwargs), timeout=60)
            return func.__name__, result
        except asyncio.TimeoutError:
            logger.warning(f"{func.__name__} 超时")
            return func.__name__, None
        except Exception as e:
            logger.error(f"{func.__name__} 出现错误: {e}")
            return func.__name__, None

    # 定义所有要并发执行的任务
    tasks = [
        #_safe_call(ascii2d_async, proxies, url),
        #_safe_call(baidu_async, proxies, url),
        #_safe_call(Copyseeker_async, proxies, url),
        #_safe_call(google_async, proxies, url),
        #_safe_call(iqdb_async, proxies, url),
        #_safe_call(iqdb3D_async, proxies, url),
        _safe_call(anime_trace,url),
        _safe_call(saucenao, url, sauceno_api,proxies),  # 替换为你的 API key
        #_safe_call(yandex_async, proxies, url),
    ]

    # 并发执行所有任务并获取结果
    results = await asyncio.gather(*tasks)

    # 转换为字典形式，方便查看各任务结果
    return {name: result for name, result in results}