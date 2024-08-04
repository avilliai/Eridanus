基于[yiri-onebot](https://github.com/YiriMiraiProject/YiriOneBot)

对项目Manyana进行重新规划，不再使用overflow作为中介，提高效率



目前任务较为繁重，目前的规划是，
- 1.将plugins中散乱的文件重新整理
- 2.重写run文件夹下各文件
- 3.优化config中配置项名称，将容易混淆的(如sparkAI等)配置项配置名改为中文
- 4.优化data文件分布

由于原先需要考虑到更新的新旧兼容问题，Manyana的许多不合理之处并不能随意更改而只能被迫保留，为了尽可能地避免在Eridantus中出现这些问题，我们将进一步调整更新时对新旧文件的处理方式。

# 开发注意事项
注意,onebot实现必须开启 reverse websocket以及配置对应的access token，默认的空值疑似将导致yirionebot出错。

yiriob目前无法在py39使用，请使用py3.11。

yiriob的默认Logger级别是DEBUG，会导致大量日志输出影响调试。你可以修改`.venv/Lib/site-packages/yiriob/utils/logger.py`
```python
logging.basicConfig(
    level=logging.INFO,           #这里，修改为logging.INFO即可。
    handlers=[RichHandler()] if RichHandler is not None else [],
)

logger = logging.getLogger("yiri-bot")

__all__ = ["logger", "pprint"]
```