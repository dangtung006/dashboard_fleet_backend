from src.helper.async_request import MyAsyncRequest
from src.helper.request import MyRequest
from src.app.app_conf import COMMON_CONF
from src.controller.robot_manager import RobotManager
from src.controller.caller_manager import CallerManager
from src.extension.db import roles, users, user_action
import httpx

HTTP_CONN = COMMON_CONF["http"]["connection"]
# https://jsonplaceholder.typicode.com/posts/3

# httpx.AsyncClient(
#     timeout=httpx.Timeout(10.0),
#     limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
# )

http_client = (
    HTTP_CONN
    == "pool"  ### pool connections # Global HTTP client (set in startup), Tạo một pool duy nhất để tránh tạo mới mỗi request
    and MyRequest(
        client=httpx.AsyncClient(
            timeout=httpx.Timeout(10.0),
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
        ),
        base_urls={
            "host_1": "https://pokeapi.co",
            "host_2": "https://jsonplaceholder.typicode.com",
        },
    )
    or MyAsyncRequest(
        base_urls={
            "host_1": "https://pokeapi.co",
            "host_2": "https://jsonplaceholder.typicode.com",
        },
    )
)


async def initAcc():
    await user_action.create_idx("expireAt")
    default_role = await roles.find_one_by_conditions({"name": "default"})
    if not default_role:

        default_resp = await roles.insert_one(
            {
                "name": "default",
                "status": 1,
                "permissions": {
                    "add": {
                        "monitor": False,
                        "robot": False,
                        "robot_detail": False,
                        "caller": False,
                        "charging_station": False,
                        "user": False,
                        "user_detail": False,
                        "statistics": False,
                    },
                    "view": {
                        "monitor": False,
                        "robot": False,
                        "robot_detail": False,
                        "caller": False,
                        "charging_station": False,
                        "user": False,
                        "user_detail": False,
                        "statistics": False,
                    },
                    "edit": {
                        "monitor": False,
                        "robot": False,
                        "robot_detail": False,
                        "caller": False,
                        "charging_station": False,
                        "user": False,
                        "user_detail": False,
                        "statistics": False,
                    },
                    "delete": {
                        "monitor": False,
                        "robot": False,
                        "robot_detail": False,
                        "caller": False,
                        "charging_station": False,
                        "user": False,
                        "user_detail": False,
                        "statistics": False,
                    },
                },
            }
        )
    admin = await roles.find_one_by_conditions({"name": "root"})
    if not admin:

        root_rol = await roles.insert_one(
            {
                "name": "root",
                "status": 1,
                "permissions": {
                    "add": {
                        "monitor": True,
                        "robot": True,
                        "robot_detail": True,
                        "caller": True,
                        "charging_station": True,
                        "user": True,
                        "user_detail": True,
                        "statistics": True,
                    },
                    "view": {
                        "monitor": True,
                        "robot": True,
                        "robot_detail": True,
                        "caller": True,
                        "charging_station": True,
                        "user": True,
                        "user_detail": True,
                        "statistics": True,
                    },
                    "edit": {
                        "monitor": True,
                        "robot": True,
                        "robot_detail": True,
                        "caller": True,
                        "charging_station": True,
                        "user": True,
                        "user_detail": True,
                        "statistics": True,
                    },
                    "delete": {
                        "monitor": True,
                        "robot": True,
                        "robot_detail": True,
                        "caller": True,
                        "charging_station": True,
                        "user": True,
                        "user_detail": True,
                        "statistics": True,
                    },
                },
            }
        )

        root_acc = await users.find_one_by_conditions({"email": "root"})

        if root_acc:
            root_acc = users.serialize(root_acc)
            # delete before create new root
            resp = await users.delete_by_id(id=root_acc["_id"])

        await users.insert_one(
            {
                "name": "Admin",
                "email": "root",
                "password": (
                    root_acc["password"]
                    if root_acc and root_acc["password"]
                    else "123456"
                ),
                "role_id": users.to_object_id(root_rol.inserted_id),  # lưu _id từ Role
                "status": "active",
            }
        )


robot_manager = RobotManager()  # Global Robot Manager instance
caller_manager = CallerManager()  # Global Caller Manager instance
