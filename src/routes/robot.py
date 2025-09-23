from fastapi import APIRouter
from src.extension.db import robots
from src.dto.robot import Robot
from src.app.app_init import robot_manager
from src.helper.response import BadRequestError, NotFoundError, SuccessResponse


robot_route = APIRouter(tags=["Robot List"])


@robot_route.get("/robot_by_id/{id}")
async def get_detail(id: str):
    resp = robot_manager.get_robot_by_id(id)

    return SuccessResponse(msg="OK").send(
        data=resp if resp else NotFoundError(msg="Robot not found").send()
    )


@robot_route.get("/get_all")
async def get_all():
    resp = robot_manager.get_all_robots()
    return SuccessResponse(msg="OK").send(
        data=resp if resp else NotFoundError(msg="Robot not found").send()
    )


@robot_route.get("/")
async def get_station_list():
    resp = await robots.find_list(page=1, page_size=10)
    robot_list = []

    async for doc in resp:
        robot_list.append(robots.serialize(doc))
    return robot_list


@robot_route.get("/count_robots")
async def count_stations():
    resp = await robots.count_by_conditions({})
    return resp


@robot_route.post("/add")
async def add(robot: Robot):
    resp = await robot_manager.add_robot(robot.dict())
    return SuccessResponse(msg="OK").send(
        data=resp if resp else NotFoundError(msg="Robot not found").send()
    )


@robot_route.put("/update/{id}")
async def update(id: str, robot: Robot):
    resp = await robot_manager.update_robot(id, robot.dict())
    return SuccessResponse(msg="OK").send(
        data=resp if resp else NotFoundError(msg="Robot not found").send()
    )


@robot_route.get("/status/{id}")
async def get_status(id: str):
    resp = robot_manager.get_robot_status_by_id(id)
    return SuccessResponse(msg="OK").send(data=resp)


@robot_route.delete("/delete/{id}")
async def remove_robot(id: str):
    resp = await robot_manager.remove_robot(id)
    return SuccessResponse(msg="OK").send(data=resp)


@robot_route.post("/control/joystick")
async def move():
    resp = await robot_manager.ctrl_joystick(
        cmd={}, robot_id="68ba97b0530bf52840ff422c"
    )
    # resp = await robot_manager.add_robot(robot.dict())
    return SuccessResponse(msg="OK").send(data=True)


@robot_route.post("/control/joystick/stop")
async def stop_move():
    resp = await robot_manager.stop_ctrl_joystick(
        cmd={}, robot_id="68ba97b0530bf52840ff422c"
    )
    # resp = await robot_manager.add_robot(robot.dict())
    return SuccessResponse(msg="OK").send(data=resp)
