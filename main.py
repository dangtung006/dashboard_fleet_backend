from fastapi_offline import FastAPIOffline
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import httpx
import threading
from async_task import listen_task
from uvicorn import Config, Server
from src.routes.index import init_app_routes
from src.app.app_init import http_client, HTTP_CONN, robot_manager, initAcc

app = FastAPIOffline(
    title="ESA ROBOT API DOCUMENT",
    description="API composed by ESA developer",
    version="1.0.0",
    contact={
        "name": "ESA",
        "url": "https://esatech.vn/",
        "email": "smartagv@esatech.vn",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

APP_HOST = "192.168.0.103"
APP_PORT = 3000


## Tạo AsyncClient khi app khởi động
@app.on_event("startup")
async def startup_event():
    await robot_manager.init_connections_from_config()

    # def run_async_from_thread():
    #     loop = asyncio.new_event_loop()
    #     asyncio.set_event_loop(loop)
    #     loop.run_until_complete(listen_task())
    #     loop.close()

    # t = threading.Thread(target=run_async_from_thread)
    # t.start()


## Đóng client đúng cách để tránh rò rỉ socket
@app.on_event("shutdown")
async def shutdown_event():
    if http_client and HTTP_CONN == "pool":
        await http_client.aclose()


async def run_server():
    config = Config(app=app, host=APP_HOST, port=APP_PORT, log_level="info")
    server = Server(config)
    await server.serve()


async def main():
    init_app_routes(app=app, host=APP_HOST, port=APP_PORT)
    await initAcc()
    await run_server()
    # await asyncio.gather(run_server())
    # await asyncio.gather(run_server(), listen_task())


if __name__ == "__main__":
    asyncio.run(main())
