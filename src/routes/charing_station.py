from fastapi import APIRouter
from src.dto.charing_station import CharingStationCreate, CharingStationInDB
from src.app.app_init import charing_station_manager

from src.helper.response import (
    BadRequestError,
    NotFoundError,
    SuccessResponse,
    InternalServerError,
)
from src.extension.db import charing_stations

charing_station_route = APIRouter(tags=["Charing Stations"])


@charing_station_route.post("/add", response_model=CharingStationInDB)
async def create_charing_station(charing: CharingStationCreate):
    try:
        req_body = charing.dict()
        resp = await charing_station_manager.add_charing_st(req_body)
        return SuccessResponse(msg="OK").send(data=resp)
    except Exception as E:
        return InternalServerError(msg=str(E))


@charing_station_route.put("/update/{charing_id}", response_model=CharingStationInDB)
async def update_charing_station(charing_id: str, charing: CharingStationCreate):
    try:
        req_body = charing.dict()
        resp = await charing_station_manager.update_charing_st(charing_id, req_body)
        return SuccessResponse(msg="OK").send(data=resp)
    except Exception as E:
        return InternalServerError(msg=str(E))


@charing_station_route.get("", response_model=list[CharingStationInDB])
async def list_charing_stations():
    try:
        resp = await charing_station_manager.get_charing_st_list()
        return SuccessResponse(msg="OK").send(data=resp)
    except Exception as E:
        print("Error listing charing stations:", E)
        return InternalServerError(msg=str(E))


@charing_station_route.get(
    "/detail/{charging_st_id}", response_model=CharingStationInDB
)
async def get_charing_station(charging_st_id: str):
    try:
        resp = await charing_station_manager.get_charing_st_by_id(charging_st_id)
        return SuccessResponse(msg="OK").send(data=resp)
    except Exception as E:
        return InternalServerError(msg=str(E))


@charing_station_route.delete("/delete/{charging_st_id}", response_model=bool)
async def delete_charing_station(charging_st_id: str):
    try:
        resp = await charing_station_manager.remove_charing_st(charging_st_id)
        return SuccessResponse(msg="OK").send(data=resp and True or False)
    except Exception as E:
        return InternalServerError(msg=str(E))
