from fastapi import APIRouter
from src.dto.robot_statistics import RobotStatistics

from src.helper.response import (
    BadRequestError,
    NotFoundError,
    SuccessResponse,
    InternalServerError,
)
from src.extension.db import robot_statistics, robots

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


@robot_statistics_route.get("/list")
async def get_robot_statistics_detail():
    try:
        resp = await robot_statistics.get_stats_with_robot()
        if not resp:
            return NotFoundError(msg="not found")

        data = [robot_statistics.serialize(doc) for doc in resp]

        # for doc in resp:
        #     print("doc::", doc)
        #     data.append(robot_statistics.serialize(doc))

        return SuccessResponse(msg="OK").send(data=data)
    except Exception as E:
        return InternalServerError(msg=str(E))
