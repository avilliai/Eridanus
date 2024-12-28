import json


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
    with open('plugins/core/gemini_func_call.json', 'r',encoding='utf-8') as f:
        data = json.load(f)
    tools = data
    return tools