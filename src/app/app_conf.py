from enum import Enum

http_connection_type = ["open_and_close", "pool"]
COMMON_CONF = {"http": {"connection": http_connection_type[0]}}


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
