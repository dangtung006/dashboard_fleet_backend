from fastapi import APIRouter
from src.extension.db import robot_stations
from src.app.app_init import http_client
import asyncio
import time

station_route = APIRouter(tags=["Robot Station"])


@station_route.get("/station_by_id/{id}")
async def get_station(id: str):
    resp = await robot_stations.find_by_id(id)
    return robot_stations.serialize(resp)


@station_route.get("/station_by_name")
async def get_station(st: str):
    # resp["_id"] = str(resp["_id"])
    # resp["created_at"] = resp["created_at"].isoformat()
    # resp["updated_at"] = resp["updated_at"].isoformat()
    resp = await robot_stations.find_one_by_conditions(conditions={"st_id": st})
    return robot_stations.serialize(resp)


@station_route.get("/station_list")
async def get_station_list():
    resp = await robot_stations.find_list(page=1, page_size=10)
    stations = []

    async for doc in resp:
        # doc["_id"] = str(doc["_id"])
        # doc["created_at"] = doc["created_at"].isoformat()
        # doc["updated_at"] = doc["updated_at"].isoformat()
        stations.append(robot_stations.serialize(doc))
    return stations


@station_route.get("/count")
async def count_stations():
    # resp = await robot_station.count_all()
    resp = await robot_stations.count_by_conditions(
        {
            "task_type": "drop_off",
        }
    )
    return resp


@station_route.get("/test/request")
async def test_req():
    resp = await http_client.get("host_2", "/posts/3")
    return http_client.to_json(resp)


@station_route.get("/test/request_multi")
async def test_req():
    start = time.perf_counter()
    # resp = await asyncio.gather(
    #     *[async_client.get("host_2", f"/posts/{i+1}") for i in range(20)]
    # )
    # print([async_client.to_json(resp[idx]) for idx in range(len(resp))])
    # for idx in range(20):
    #     post = await async_client.get("host_2", f"/posts/{idx+1}")

    # async for resp in async_client.next_get(10, "host_2", "/posts/"):
    #     print(resp)

    print("aaaaaaaaaa")
    end = time.perf_counter()
    print(f"Thời gian chạy: {end - start:.6f} giây")
    return "hahaha"
