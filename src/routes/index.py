from fastapi import APIRouter
from src.routes.station import station_route
from src.routes.robot import robot_route
from src.routes.caller import caller_route
from src.routes.role import role_route
from src.routes.user import user_route
from src.routes.auth import auth_route
from src.routes.map import robot_maps_route
from src.routes.charing_station import charing_station_route

from src.routes.ws import ws_router

route_conf = [
    {
        "name": "/robot",
        "route": robot_route,
        "has_sub": [
            # {"name": "/status", "route": status_routes},
            # {"name": "/nav", "route": nav_routes},
            # {"name": "/other", "route": other_routes},
            # {"name": "/conf", "route": conf_routes},
            # {"name": "/ctrl", "route": ctrl_routes},
            # {"name": "/station", "route": station_routes},
            # {"name": "/map", "route": map_routes},
        ],
    },
    {"name": "/station", "route": station_route, "has_sub": []},
    {"name": "/role", "route": role_route, "has_sub": []},
    {"name": "/user", "route": user_route, "has_sub": []},
    {"name": "/caller", "route": caller_route, "has_sub": []},
    {"name": "/auth", "route": auth_route, "has_sub": []},
    {"name": "/robot_map", "route": robot_maps_route, "has_sub": []},
    {"name": "/charing_station", "route": charing_station_route, "has_sub": []},
]


def init_app_routes(app: APIRouter, host: str, port: int):
    print(f"[Server Docs At]  : http://{host}:{port}/docs")
    # app.include_router(ws_router, prefix="/ws")
    app.include_router(ws_router)

    for idx in range(len(route_conf)):
        item_router_conf = route_conf[idx]
        item_router: APIRouter = item_router_conf["route"]
        item_router_prefix = item_router_conf["name"]

        if len(route_conf[idx]["has_sub"]) > 0:
            for jdx in range(len(route_conf[idx]["has_sub"])):
                sub_route = route_conf[idx]["has_sub"][jdx]
                route = sub_route["route"]
                prefix = sub_route["name"]
                item_router.include_router(route, prefix=prefix)

        app.include_router(item_router, prefix=item_router_prefix)
