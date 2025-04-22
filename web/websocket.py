import asyncio
import websockets
import json
import time
import random

# 用于存储所有已连接的 WebSocket 客户端
clients = set()

async def handle_connection(websocket):
    print("WebSocket 客户端已连接")
    clients.add(websocket)

    try:
        # 发送连接成功消息
        #await websocket.send(json.dumps({'time': 1739849686, 'self_id': 3377428814, 'post_type': 'meta_event', 'meta_event_type': 'lifecycle', 'sub_type': 'connect'}))

        while True:
            # 接收来自前端的消息
            message = await websocket.recv()
            print(f"收到前端消息: {message} {type(message)}")
            message = json.loads(message)
            if "echo" in message:
                for client in clients:
                    await client.send(json.dumps({'status': 'ok',
                                       'retcode': 0,
                                       'data': {'message_id': 1253451396},
                                       'message': '',
                                       'wording': '',
                                       'echo': message['echo']}))



            if isinstance(message,list):

                message.insert(0,{'type': 'at', 'data': {'qq': '1000000', 'name': 'Eridanus'}})

            print(message, type(message))

            onebot_event = {
                'self_id': 1000000,
                'user_id': 111111111,
                'time': int(time.time()),
                'message_id': 1253451396,
                'real_id': 1253451396,
                'message_seq': 1253451396,
                'message_type': 'group',
                'sender':
                    {'user_id': 111111111, 'nickname': '主人', 'card': '', 'role': 'member', 'title': ''},
                'raw_message': "",
                'font': 14,
                'sub_type': 'normal',
                'message': message,
                'message_format': 'array',
                'post_type': 'message',
                'group_id': 879886836}

            event_json = json.dumps(onebot_event, ensure_ascii=False)

            # 发送给所有连接的客户端（后端）
            for client in clients:
                if client != websocket:  # 避免回传给前端
                    await client.send(event_json)


            print(f"已发送 OneBot v11 事件: {event_json}")
    except websockets.exceptions.ConnectionClosed as e:
        print(f"客户端连接关闭: {e}")
    finally:
        print("WebSocket 客户端断开连接")
        clients.remove(websocket)

# 启动 WebSocket 服务器
async def start_server():
    server = await websockets.serve(handle_connection, "0.0.0.0", 5008)
    print("WebSocket 服务端已启动，在 5008 端口监听...")
    await server.wait_closed()

# 使用 asyncio.run 启动服务
if __name__ == "__main__":

    asyncio.run(start_server())
