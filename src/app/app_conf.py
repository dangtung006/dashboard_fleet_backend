import os
from enum import Enum
from dotenv import load_dotenv

load_dotenv()

SERVER_IP = os.getenv("SERVER_IP")
SERVER_PORT = os.getenv("SERVER_PORT")
IP_ROBOT = os.getenv("IP_ROBOT")

http_connection_type = ["open_and_close", "pool"]


class USER_AUTH_TYPE(Enum):
    VIEW = "view"
    UPDATE = "edit"
    ADD = "add"
    REMOVE = "remove"


class USER_AUTH_RESOURCE(Enum):
    USER = "user"
    CALLER = "caller"
    ROBOT = "robot"
    STATIC = "statistics"


COMMON_CONF = {
    "app": {
        "host": SERVER_IP,
        "port": int(SERVER_PORT),
        "debug": True,
        "use_reloader": False,
        "valid_origin": ["http://localhost:3000"],
    },
    "http": {"connection": http_connection_type[0]},
}
