from fastapi import APIRouter
from src.extension.db import callers
from src.dto.caller import CallerCreate, CallerInDB
from src.app.app_init import caller_manager
from src.helper.response import BadRequestError, NotFoundError, SuccessResponse


caller_route = APIRouter(tags=["Callers"])


@caller_route.get("/caller_by_id/{id}", response_model=CallerInDB)
async def get_detail(id: str):
    resp = await caller_manager.get_caller_by_id(id)
    return SuccessResponse(msg="OK").send(data=resp and resp or None)


@caller_route.get("/get_all", response_model=list[CallerInDB])
async def get_all():
    resp = await caller_manager.get_caller_list()
    return SuccessResponse(msg="OK").send(data=resp)


@caller_route.get("/", response_model=list[CallerInDB])
async def get_station_list():
    resp = await callers.find_list(page=1, page_size=10)
    robot_list = []

    async for doc in resp:
        robot_list.append(callers.serialize(doc))
    return robot_list


@caller_route.post("/add", response_model=CallerInDB)
async def add(
    caller: CallerCreate,
):
    resp = await caller_manager.add_caller(caller.dict())
    return SuccessResponse(msg="OK").send(data=resp)


@caller_route.put("/update/{id}", response_model=CallerInDB)
async def update(id: str, caller: CallerCreate):
    resp = await caller_manager.update_caller(id, caller.dict())
    return SuccessResponse(msg="OK").send(
        data=resp if resp else NotFoundError(msg="Robot not found").send()
    )


@caller_route.delete("/delete/{id}", response_model=bool)
async def remove_robot(id: str):
    resp = await caller_manager.remove_caller(id)
    return SuccessResponse(msg="OK").send(data=resp and True or False)
