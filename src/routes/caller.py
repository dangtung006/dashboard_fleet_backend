from fastapi import APIRouter
from src.extension.db import robots
from src.dto.caller import Caller
from src.app.app_init import caller_manager
from src.helper.response import BadRequestError, NotFoundError, SuccessResponse


caller_route = APIRouter(tags=["Callers"])


@caller_route.get("/robot_by_id/{id}")
async def get_detail(id: str):
    resp = caller_manager.get_caller_by_id(id)

    return SuccessResponse(msg="OK").send(
        data=resp if resp else NotFoundError(msg="Robot not found").send()
    )


@caller_route.get("/get_all")
async def get_all():
    resp = caller_manager.get_all_caller()
    return SuccessResponse(msg="OK").send(data=resp)


@caller_route.get("/")
async def get_station_list():
    resp = await robots.find_list(page=1, page_size=10)
    robot_list = []

    async for doc in resp:
        robot_list.append(robots.serialize(doc))
    return robot_list


@caller_route.get("/count_callers")
async def count_stations():
    resp = await robots.count_by_conditions({})
    return resp


@caller_route.post("/add")
async def add(caller: Caller):
    resp = await caller_manager.add_caller(caller.dict())
    return SuccessResponse(msg="OK").send(data=resp)


@caller_route.put("/update/{id}")
async def update(id: str, caller: Caller):
    resp = await caller_manager.update_caller(id, caller.dict())
    return SuccessResponse(msg="OK").send(
        data=resp if resp else NotFoundError(msg="Robot not found").send()
    )


@caller_route.delete("/delete/{id}")
async def remove_robot(id: str):
    resp = await caller_manager.remove_caller(id)
    return SuccessResponse(msg="OK").send(data=resp)
