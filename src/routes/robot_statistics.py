from fastapi import APIRouter
from src.dto.robot_statistics import RobotStatistics

from src.helper.response import (
    BadRequestError,
    NotFoundError,
    SuccessResponse,
    InternalServerError,
)
from src.extension.db import robot_statistics

robot_statistics_route = APIRouter(tags=["Robot Statistics"])


@robot_statistics_route.get("/sumary", response_model=list[RobotStatistics])
async def get_sumary_statistics():
    try:
        resp = await robot_statistics.find_list(page=1, page_size=10)
        roleList = []

        async for doc in resp:
            roleList.append(robot_statistics.serialize(doc))

        return SuccessResponse(msg="OK").send(data=roleList)
    except Exception as E:
        return InternalServerError(msg=str(E))


@robot_statistics_route.get("/detail/{robot_id}")
async def get_robot_statistics_detail(robot_id: str):
    try:
        resp = await robot_statistics.find_by_id(id=robot_id)
        if not resp:
            return NotFoundError(msg="Role not found")
        return SuccessResponse(msg="OK").send(data=resp)
    except Exception as E:
        return InternalServerError(msg=str(E))
