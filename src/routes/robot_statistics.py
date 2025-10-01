from fastapi import APIRouter
from src.dto.robot_statistics import RobotStatisticsCreate, RobotStatisticsUpdate

from src.helper.response import (
    BadRequestError,
    NotFoundError,
    SuccessResponse,
    InternalServerError,
)
from src.extension.db import robot_statistics, robots

robot_statistics_route = APIRouter(tags=["Robot Statistics"])


@robot_statistics_route.get("/sumary", response_model=list[RobotStatisticsUpdate])
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


@robot_statistics_route.post("/control/seed")
async def add_statistic(robot: RobotStatisticsCreate):
    robot_id = robot.robot_id
    print(robot_id)
    resp = await robot_statistics.insert_one(
        {
            "robot_id": robot_statistics.to_object_id(robot.robot_id),
            "date": robot.date.strftime("%Y-%m-%d"),
            "runtime_hours": robot.runtime_hours,
            "distance_traveled": robot.distance_traveled,
            "error_count": robot.error_count,
            "status_distribution": robot.status_distribution,
        }
    )
    print("resp:", resp.inserted_id)
    # if not resp:
    #     return InternalServerError(msg="Insert statistic failed")
    return SuccessResponse(msg="OK").send(data=True)
