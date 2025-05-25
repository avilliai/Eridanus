# AI生成的插件代码
# 生成时间: 2025-05-25 21:18:39

import asyncio
from developTools.event.events import GroupMessageEvent, PrivateMessageEvent
from developTools.message.message_components import Text, Image
from framework_common.framework_util.hot_reload import event_handler
from framework_common.database_util.User import get_user
from framework_common.database_util.User import get_user
from framework_common.framework_util.websocket_fix import ExtendBot
from framework_common.framework_util.yamlLoader import YAMLManager
from developTools.message.message_components import Text, Image
import asyncio
from developTools.event.events import GroupMessageEvent, PrivateMessageEvent
from developTools.message.message_components import Text, Image
from framework_common.framework_util.hot_reload import event_handler
from framework_common.database_util.User import get_user # Included as per example template
from framework_common.framework_util.websocket_fix import ExtendBot
from framework_common.framework_util.yamlLoader import YAMLManager
import traceback
import aiohttp
import json

plugin_name = "WeatherQuery"

async def get_weather_from_api(city_name: str):
    """
    Fetches weather data from the API.
    Uses aiohttp with params for proper URL encoding.
    """
    base_url = "https://v2.xxapi.cn/api/weather"
    params = {'city': city_name}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url, params=params, timeout=10) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"API request for {city_name} failed with status {response.status}: {error_text}")
                    # Try to parse error text if it's JSON
                    try:
                        error_json = json.loads(error_text)
                        return error_json # Return the error JSON from API if available
                    except json.JSONDecodeError:
                        return {"code": response.status, "msg": f"API request failed with status {response.status}."} # Generic error
                
                # Check content type before parsing as JSON
                content_type = response.headers.get('Content-Type', '').lower()
                if 'application/json' not in content_type:
                    raw_text = await response.text()
                    print(f"API response for {city_name} is not JSON. Content-Type: {content_type}. Body: {raw_text}")
                    return {"code": 500, "msg": "API response format error (not JSON)."}

                data = await response.json()
                return data
    except aiohttp.ClientConnectorError as e:
        print(f"Network error fetching weather data for {city_name}: {e}")
        return {"code": 503, "msg": "Network error, unable to connect to weather service."}
    except aiohttp.ClientError as e: # General aiohttp client error
        print(f"Client error fetching weather data for {city_name}: {e}")
        return {"code": 500, "msg": "Client error while fetching weather data."}
    except asyncio.TimeoutError:
        print(f"Timeout fetching weather data for {city_name}.")
        return {"code": 504, "msg": "Request to weather service timed out."}
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response for {city_name}: {e}.")
        return {"code": 500, "msg": "Error decoding weather data from API."}
    except Exception as e:
        print(f"An unexpected error occurred while fetching weather for {city_name}: {e}")
        traceback.print_exc()
        return {"code": 500, "msg": "An unexpected error occurred while fetching weather."}

async def format_weather_response(weather_json_data, city_name_query: str) -> str:
    """Formats the weather JSON data into a readable string, incorporating persona."""
    if weather_json_data is None: # Should ideally not happen if get_weather_from_api returns error dicts
        return f"抱歉主人，未能获取到{city_name_query}的天气数据，可能是网络问题或API暂时不可用。"

    # Check for API's own error code or if 'data' field is missing/malformed
    if weather_json_data.get("code") != 200:
        error_msg = weather_json_data.get("msg", f"无法获取{city_name_query}的天气信息或城市不存在。")
        return f"抱歉主人，{error_msg}"

    data_content = weather_json_data.get("data")
    if not isinstance(data_content, dict):
        return f"抱歉主人，获取到的{city_name_query}天气数据格式不正确 (missing 'data' object)。"

    city_from_api = data_content.get("city", city_name_query)
    daily_forecasts = data_content.get("data", []) # This is the list of forecasts

    if not isinstance(daily_forecasts, list) or not daily_forecasts:
        # Check if the API returned a specific message for no data for this city
        api_msg = data_content.get("msg") # Some APIs might put a message here
        if api_msg and city_from_api in api_msg: # Heuristic
             return f"抱歉主人，{api_msg}"
        return f"抱歉主人，{city_from_api} 未来几天暂无天气预报数据。"

    message_parts = [f"主人，这是{city_from_api}的天气预报喵："]
    for day_data in daily_forecasts:
        if not isinstance(day_data, dict):
            print(f"Skipping malformed day_data entry: {day_data}")
            continue

        date = day_data.get("date", "日期未知")
        temperature = day_data.get("temperature", "温度未知")
        weather = day_data.get("weather", "天气未知")
        wind = day_data.get("wind", "风力未知")
        air_quality = day_data.get("air_quality", "空气质量未知")
        message_parts.append(
            f"{date}: {weather}, 温度: {temperature}, 风力: {wind}, 空气质量: {air_quality}"
        )
    return "\n".join(message_parts)

async def weather_query_logic(bot: ExtendBot, event: GroupMessageEvent, config: YAMLManager):
    """
    Core logic for handling weather queries.
    This function is called by the event handler in main.
    """
    message_text = str(event.pure_text).strip()
    command_prefix = "查询天气"

    if message_text.startswith(command_prefix):
        city_name_part = message_text[len(command_prefix):].strip()
        
        if not city_name_part:
            await bot.send(event, Text("主人，请告诉我您想查询哪个城市的天气喵？例如：查询天气北京"))
            return

        city_name = city_name_part
        
        # Send initial acknowledgement
        # Removed initial "正在查询" message to reduce spam, will send result or error directly.
        # await bot.send(event, Text(f"收到喵！正在为主人查询{city_name}的天气信息，请稍候..."))

        weather_json = await get_weather_from_api(city_name)
        formatted_message_str = await format_weather_response(weather_json, city_name)
        
        await bot.send(event, Text(formatted_message_str))

def main(bot: ExtendBot, config: YAMLManager):
    try:
        @bot.on(GroupMessageEvent)
        async def GroupMessageHandler(event: GroupMessageEvent):
            try:
                await weather_query_logic(bot, event, config)
            except Exception as e:
                print(f"Error during weather_query_logic execution for event {event.message_id}: {e}")
                traceback.print_exc()
                try:
                    # Send a generic error message to the user, incorporating persona
                    await bot.send(event, Text("呜喵...处理主人的天气查询请求时遇到了一点小麻烦，请稍后再试吧！"))
                except Exception as send_e:
                    print(f"Critical error: Failed to send error message to user: {send_e}")

        # If there were other handlers or setup, they would go here.
        # print(f"✅ {plugin_name}插件加载成功。天气查询功能已激活。") # Optional: log success

    except Exception as e:
        print(f"❌ {plugin_name}插件加载失败: {e}")
        traceback.print_exc()
