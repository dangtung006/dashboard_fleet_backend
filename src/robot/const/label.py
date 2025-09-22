from enum import Enum


class CONFIDENCE_AJUST(Enum):
    BAD = 0.3
    AVERAGE = 0.5
    GOOD = 0.8


class TASK_STATUS(Enum):
    NONE = 0
    WAITING = 1
    RUNNING = 2  ### navigation running
    SUSPENDED = 3  ### navigation pause
    COMPLETED = 4  ### navigation finished
    FAILED = 5
    CANCELED = 6  ### navigation canceled


class TASK_TYPE(Enum):
    NO_NAVIGATION = 0


class BLOCK_REASON(Enum):
    ULTRASONIC = 0
    LASER = 1
    FALLINGDOWN = 2
    COLLISION = 3
    INFRARED = 4
    LOCK = 5
    DYNAMIC_OBSTACLE = 6
    VIRTUAL_LASER = 7
    CAMERA_3D = 8
    RANGE_SENSOR = 9
    DI_ULTRASONIC = 10


class LOAD_MAP_PROCESS(Enum):
    FAILED = 0
    SUCCESS = 1
    LOADING = 2


class LOCALIZATION_PROCESS(Enum):
    FAILED = 0
    SUCCESS = 1
    RELOCING = 2
    COMPLETED = 3


class NAVIGATION_PROCESS(Enum):
    NO_NAVIGATE = 0
    FREE_NAV_TO_COORDINATE = 1
    FREE_NAV_TO_STATION = 2
    PATH_TO_STATION = 3
    ROTATION = 7
    OTHER = 100
