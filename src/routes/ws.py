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


@ws_router.websocket("/robot/{robot_id}")
async def get_robot_status_by_id(robot_id: str, ws: WebSocket):
    await ws.accept()

    while True:
        try:
            data = robot_manager.get_robot_by_id(robot_id)
            await ws.send_json(data)
            await asyncio.sleep(1)
        except WebSocketDisconnect as Err:
            pass
        except WebSocketException as Err:
            print(str(Err))
        except RuntimeError:
            break


@ws_router.websocket("/robot_stats/recent")
async def get_robot_status_stats(ws: WebSocket):
    await ws.accept()

    while True:
        try:
            data = robot_manager.get_recent_stats()
            await ws.send_json(data)
            await asyncio.sleep(1)
        except WebSocketDisconnect as Err:
            pass
        except WebSocketException as Err:
            print(str(Err))
        except RuntimeError:
            break


@ws_router.websocket("/joystick")
async def handle_control_joystick(ws: WebSocket):
    await ws.accept()

    while True:
        try:
            cmd = await ws.receive_json()
            await robot_manager.ctrl_joystick(cmd)
        except WebSocketDisconnect as Err:
            pass
        except WebSocketException as Err:
            print(str(Err))
        except RuntimeError:
            break
