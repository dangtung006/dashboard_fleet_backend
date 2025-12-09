from src.helper.async_request import MyAsyncRequest
from src.helper.request import MyRequest
from src.app.app_conf import COMMON_CONF
from src.controller.robot_manager import RobotManager
from src.controller.caller_manager import CallerManager
from src.controller.charging_station_manager import CharingStationManager
from src.extension.db import roles, users, user_action, robot_statistics
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

    #### khởi tạo role mặc định và admin
    await roles.find_one_and_update(
        {"name": "default"},
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
        },
        upsert=True,
        # return_document=True,  # Return the updated document
    )
    admin_role = await roles.find_one_and_update(
        {"name": "admin"},
        {
            "name": "admin",
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
        },
        upsert=True,
        # return_document=True,  # Return the updated document
    )

    admin_role = roles.serialize(admin_role)
    root_acc = await users.find_one_by_conditions({"email": "root@admin.com"})

    if not root_acc:
        await users.insert_one(
            {
                "name": "admin",
                "email": "root@admin.com",
                "password": "123456",
                "role_id": users.to_object_id(admin_role["id"]),  # lưu _id từ Role
                "status": "active",
            },
        )
    print("Inited root account:::", root_acc)


robot_manager = RobotManager()  # Global Robot Manager instance
caller_manager = CallerManager()  # Global Caller Manager instance
charing_station_manager = (
    CharingStationManager()
)  # Global charging station Manager instance
