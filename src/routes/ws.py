from fastapi import APIRouter, WebSocket, WebSocketDisconnect, WebSocketException
import asyncio

ws_router = APIRouter()
from src.app.app_init import robot_manager


@ws_router.websocket("/robots")
async def get_robot_status(ws: WebSocket):
    await ws.accept()

    while True:
        try:
            data = robot_manager.get_all_robots()
            await ws.send_json(data)
            await asyncio.sleep(1)
        except WebSocketDisconnect as Err:
            pass
        except WebSocketException as Err:
            print(str(Err))
        except RuntimeError:
            break


@ws_router.websocket("/joystick")
async def get_robot_status(ws: WebSocket):
    await ws.accept()

    while True:
        try:
            cmd = await ws.receive_json()
            await robot_manager.ctrl_joystick(cmd, "68ba97b0530bf52840ff422c")
        except WebSocketDisconnect as Err:
            pass
        except WebSocketException as Err:
            print(str(Err))
        except RuntimeError:
            break
