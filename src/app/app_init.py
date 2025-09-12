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
    admin = await roles.find_one_by_conditions({"name": "root"})
    if not admin:

        root_rol = await roles.insert_one(
            {
                "name": "root",
                "permissions": {
                    "add": {
                        "charging_station": True,
                        "dashboard": True,
                        "robot": True,
                        "robot_information": True,
                        "role_and_permission": True,
                        "statics": True,
                        "user": True,
                        "user_information": True,
                    },
                    "view": {
                        "charging_station": True,
                        "dashboard": True,
                        "robot": True,
                        "robot_information": True,
                        "role_and_permission": True,
                        "statics": True,
                        "user": True,
                        "user_information": True,
                    },
                    "edit": {
                        "charging_station": True,
                        "dashboard": True,
                        "robot": True,
                        "robot_information": True,
                        "role_and_permission": True,
                        "statics": True,
                        "user": True,
                        "user_information": True,
                    },
                    "delete": {
                        "charging_station": True,
                        "dashboard": True,
                        "robot": True,
                        "robot_information": True,
                        "role_and_permission": True,
                        "statics": True,
                        "user": True,
                        "user_information": True,
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
