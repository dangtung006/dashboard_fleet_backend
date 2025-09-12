import asyncio
from src.app.app_init import http_client


async def wait_util_time(time=10):
    for i in range(time):
        print(f"time slap {i} s")
        await asyncio.sleep(1)


async def listen_task():
    while True:
        resp = await http_client.get("host_2", "/posts/1")
        print(http_client.to_json(resp))
        await asyncio.sleep(2)
