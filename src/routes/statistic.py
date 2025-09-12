from fastapi import APIRouter
from src.extension.db import robots
from src.dto.robot import Robot

robot_route = APIRouter(tags=["Robot List"])


@robot_route.get("/robot_by_id/{id}")
async def get_station(robot: Robot, id: str):
    resp = await robots.find_by_id(id)
    return robots.serialize(resp)

@robot_route.get("/get_all")
async def get_all():
    resp = await robots.find_all()
    return robots.serialize(resp)

@robot_route.get("/")
async def get_station_list():
    resp = await robots.find_list(page=1, page_size=10)
    robot_list = []

    async for doc in resp:
        # doc["_id"] = str(doc["_id"])
        # doc["created_at"] = doc["created_at"].isoformat()
        # doc["updated_at"] = doc["updated_at"].isoformat()
        robot_list.append(robots.serialize(doc))
    return robot_list

@robot_route.get("/count_robots")
async def count_stations():
    # resp = await robot_station.count_all()
    resp = await robots.count_by_conditions({})
    return resp

@robot_route.get("/add")
async def add(robot: Robot):
    resp = await robots.insert_one(robot.dict())
    return resp

@robot_route.get("/update")
async def update(robot: Robot, id: str):
    resp = await robots.update_one(
        {"_id": robots.to_object_id(id)}, {"$set": robot.dict()}
    )
    return resp


