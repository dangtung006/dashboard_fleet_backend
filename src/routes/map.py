from fastapi import APIRouter
from src.dto.map import RobotMapCreate, RobotMapInDB
from bson import ObjectId

from src.helper.response import (
    BadRequestError,
    NotFoundError,
    SuccessResponse,
    InternalServerError,
)
from src.extension.db import robot_maps

robot_maps_route = APIRouter(tags=["Maps"])


@robot_maps_route.get("")
async def list_maps():
    try:
        pipeline = [
            {
                "$lookup": {
                    "from": "robots",  # tên collection robot
                    "localField": "robots_in_use",  # field trong map (có thể là list)
                    "foreignField": "_id",  # field trong robot
                    "as": "robot_in_use_info",  # alias chứa danh sách robot match
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "map_name": 1,
                    "map_desc": 1,
                    "map_date": 1,
                    "map_status": 1,
                    "map_json_data": 1,
                    "robot_in_use_info.robot_name": 1,
                    "robot_in_use_info.robot_ip": 1,
                    "robot_in_use_info._id": 1,
                }
            },
        ]

        resp = await robot_maps.collection.aggregate(pipeline).to_list(length=100)
        data = [robot_maps.serialize(doc) for doc in resp]
        return SuccessResponse(msg="OK").send(data=data)

    except Exception as E:
        print("EEEE::::::", str(E))
        return InternalServerError(msg=str(E))


@robot_maps_route.get("/{map_id}", response_model=RobotMapInDB)
async def get_map(map_id: str):
    try:
        # resp = await robot_maps.find_by_id(id=map_id)

        pipeline = [
            {"$match": {"_id": ObjectId(map_id)}},
            {
                "$lookup": {
                    "from": "robots",  # tên collection robot
                    "localField": "robots_in_use",  # field trong map (có thể là list)
                    "foreignField": "_id",  # field trong robot
                    "as": "robot_in_use_info",  # alias chứa danh sách robot match
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "map_name": 1,
                    "map_desc": 1,
                    "map_date": 1,
                    "map_json_data": 1,
                    "robot_in_use_info.robot_name": 1,
                    "robot_in_use_info.robot_ip": 1,
                    "robot_in_use_info._id": 1,
                }
            },
        ]

        resp = await robot_maps.collection.aggregate(pipeline).to_list(1)
        data = [robot_maps.serialize(doc) for doc in resp]
        data = len(data) > 0 and data[0] or None

        if not data:
            return NotFoundError(msg="not found")
        return SuccessResponse(msg="OK").send(data=data)

    except Exception as E:
        return InternalServerError(msg=str(E))


@robot_maps_route.post("/add", response_model=RobotMapInDB)
async def create_map(map: RobotMapCreate):

    try:
        # print("map::", map.dict())
        req_body = map.dict()
        resp = await robot_maps.insert_one(req_body)
        inserted_id = str(resp.inserted_id)
        data = (
            inserted_id
            and robot_maps.serialize({**req_body, "_id": inserted_id})
            or None
        )

        return SuccessResponse(msg="OK").send(data=data)

    except Exception as E:
        print(E)
        return InternalServerError(msg=str(E))


@robot_maps_route.put("/update/{map_id}", response_model=RobotMapInDB)
async def update_map(map_id: str, robotMap: RobotMapCreate):
    try:
        req_body = robotMap.dict()
        data = await robot_maps.find_by_id(id=map_id)

        resp = await robot_maps.find_one_and_update(
            {"_id": robot_maps.to_object_id(map_id)}, req_body
        )

        data = robot_maps.serialize(resp)

        return SuccessResponse(msg="OK").send(data=data)

    except Exception as E:
        return InternalServerError(msg=str(E))


@robot_maps_route.delete("/delete/{map_id}", response_model=bool)
async def delete_map(map_id: str):
    try:

        resp = await robot_maps.delete_by_id(map_id)
        if resp.deleted_count == 0:
            return BadRequestError(msg="Role not found")

        return SuccessResponse(msg="OK").send(data=True)
    except Exception as E:
        return InternalServerError(msg=str(E))


@robot_maps_route.patch("/push_robot/multi/{map_id}")
async def load_map_to_robots(map_id: str, robots: list[str]):
    list_of_ids = [robot_maps.to_object_id(id) for id in robots]
    resp = await robot_maps.update_one(
        {"_id": robot_maps.to_object_id(map_id)},
        {"robots_in_use": list_of_ids},
    )
    return SuccessResponse(msg="OK").send(data=True)


@robot_maps_route.patch("/unload_map/{map_id}/{robot}")
async def unload_map_to_robot(map_id: str, robot: str):

    resp = await robot_maps.update_one_v2(
        {"_id": robot_maps.to_object_id(map_id)},
        # {"$addToSet": {"robots_in_use": {"$each": list_of_ids}}},
        {"$pull": {"robots_in_use": robot_maps.to_object_id(robot)}},
    )
    return SuccessResponse(msg="OK").send(data=True)
