#为func_calling提供函数映射
import inspect
import json

from plugins.basic_plugin.weather_query import weather_query
def func_map():
    tools=[
        {
          "type": "function",
          "function": {
            "name": "weather_query",
            "description": "Get the current weather in a given location",
            "parameters": {
              "type": "object",
              "properties": {
                "location": {
                  "type": "string",
                  "description": "The city and state, e.g. 上海"
                },
              },
              "required": ["location"]
            }
          }
        }
      ]
    return tools

def gemini_func_map():
    tools=[{
        "google_search_retrieval": {
            "dynamic_retrieval_config": {
                "mode": "MODE_DYNAMIC",
                "dynamic_threshold": 1,
            }
        }
    }]
    return tools

async def call_func(func_name, params):
    """
    动态调用已导入的函数。

    参数:
        func_name (str): 函数名。
        params (str): JSON 字符串，包含函数参数。

    返回:
        异步函数的返回值。
    """
    # 从全局作用域中获取函数对象
    func = globals().get(func_name)

    if func is None:
        raise ValueError(f"Function '{func_name}' not found.")

    # 检查是否为可调用对象
    if not callable(func):
        raise TypeError(f"'{func_name}' is not callable.")

    # 检查是否为异步函数
    if not inspect.iscoroutinefunction(func):
        raise TypeError(f"'{func_name}' is not an async function.")

    # 将 JSON 字符串解析为字典
    try:
        params_dict = json.loads(params)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON string for parameters: {e}")

    # 调用函数并传入参数
    return await func(**params_dict)