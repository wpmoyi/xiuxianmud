# -*- coding: utf-8 -*-
"""
P1 · 第一个 Python 服务器（WebSocket 回显服务器）

作用：
    收到客户端发来的任意消息后，回一句「你说：xxx」。
    这是打通「浏览器/手机 ↔ 服务器」链路的最小实现。

运行方法（在 server 目录下）：
    1) 安装依赖：  pip install -r requirements.txt
    2) 启动服务器：python main.py
    3) 看到「服务器已启动，监听 0.0.0.0:8765」即成功。

要点：
    必须监听 0.0.0.0（所有网卡），写成 127.0.0.1 手机就连不上。
"""

import asyncio
import json

# websockets 13 起推荐用 asyncio 版本；经典 websockets.serve 在新版已移除。
from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosed

# 监听地址与端口。
# 0.0.0.0 = 监听本机所有网卡，手机通过电脑局域网 IP 才能连进来。
HOST = "0.0.0.0"
PORT = 8765


def parse_text(raw):
    """把收到的原始消息转成文本。

    客户端按协议发送 JSON：{"type": "command", "text": "..."}。
    如果解析失败，就退化成「直接把原始字符串当文本」。
    """
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8", errors="replace")
    try:
        data = json.loads(raw)
        if isinstance(data, dict) and "text" in data:
            return str(data["text"])
    except (json.JSONDecodeError, TypeError):
        pass
    return raw


async def handle(websocket):
    """处理单个客户端连接：收到什么就回什么。"""
    remote = websocket.remote_address
    print(f"[连接] {remote} 已连上")

    try:
        # async for：一直等待并逐条接收这个连接发来的消息。
        async for raw in websocket:
            text = parse_text(raw)
            # 按协议回一个 JSON 消息；ensure_ascii=False 让中文原样输出。
            reply = {"type": "text", "text": f"你说：{text}"}
            await websocket.send(json.dumps(reply, ensure_ascii=False))
            print(f"[收到] {remote}: {text}")
    except ConnectionClosed:
        pass

    print(f"[断开] {remote} 已断开")


async def main():
    print(f"服务器已启动，监听 {HOST}:{PORT}")
    print("浏览器或手机打开客户端页面，输入内容即可看到回显。")
    # serve() 返回服务器对象，用 async with 管理它的生命周期。
    async with serve(handle, HOST, PORT):
        # asyncio.Future() 永不结束，让服务器一直运行，直到按 Ctrl+C。
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n服务器已停止。")
