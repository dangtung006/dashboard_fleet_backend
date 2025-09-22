import asyncio
import struct
import json

from src.robot.conf import status, navigation, other, config, control

PACK_FMT_STR = "!BBHLH6s"
HEADER_SIZE = struct.calcsize(PACK_FMT_STR)
REQ_ID = 1


class API_GROUP:
    navigation = "nav"
    status = "status"
    control = "ctrl"
    conf = "conf"
    other = "other"


class ROBOT_RESPONSE:
    success = 0
    request_err = 1
    resp_time_out = 2
    read_pack_err = 3
    unknown_reason = 4


class RobotSocketConnection:
    def __init__(self, ip: str, port: int, name: str, retry_interval: float = 5.0):

        self.ip = ip
        self.port = port
        self.name = name
        self.retry_interval = retry_interval
        self.connected = False
        self.lock = asyncio.Lock()
        self.conn = None

    async def connect(self):
        while not self.connected:
            try:
                reader, writer = await asyncio.open_connection(self.ip, self.port)
                self.connected = True
                print(f"[{self.name}] Connected to {self.ip}:{self.port}")
                self.conn = (reader, writer)
            except Exception as e:
                print(
                    f"[{self.name}] Failed to connect: {e}. Retrying in {self.retry_interval}s"
                )
                await asyncio.sleep(self.retry_interval)

    def build_packet(self, req_id, msg_type, msg):
        json_str = json.dumps(msg)
        msg_len = len(json_str.encode("utf-8"))
        header = struct.pack(
            PACK_FMT_STR, 0x5A, 0x01, req_id, msg_len, msg_type, b"\x00" * 6
        )
        return header + json_str.encode("utf-8")

    def unpack_header(self, data):
        return struct.unpack(PACK_FMT_STR, data)

    async def send_request(self, key, req_id, msg_type, msg, timeout=5):

        reader, writer = self.conn

        if not reader or not writer:
            # return None
            return ROBOT_RESPONSE.unknown_reason

        packet = self.build_packet(req_id, msg_type, msg)

        try:
            writer.write(packet)
            await writer.drain()
        except (ConnectionResetError, BrokenPipeError, OSError) as e:
            print(
                f"[{key}]- action_type: {msg_type}🔌 Send failed: {e}. Reconnecting..."
            )
            # await self.connect(key)
            await asyncio.sleep(1)
            return await self.send_request(key, req_id, msg_type, msg, timeout)

        try:
            header = await asyncio.wait_for(reader.readexactly(HEADER_SIZE), timeout)

            m_sync, m_ver, m_serial, m_length, m_type, m_reserved = self.unpack_header(
                header
            )

            if m_length > 0:
                payload = await asyncio.wait_for(reader.readexactly(m_length), timeout)
                response = json.loads(payload.decode("utf-8"))
                return response

            return ROBOT_RESPONSE.unknown_reason
            # return None

        except asyncio.TimeoutError:
            print(f"[{key}] ⏱ Timeout waiting for response")
            # return None
            return ROBOT_RESPONSE.resp_time_out
        except asyncio.IncompleteReadError:
            print(f"[{key}] 🔌 Connection closed during read")
            # await self.connect(key)
            # return None
            return ROBOT_RESPONSE.read_pack_err
        except Exception as e:
            print(f"[{key}] ❌ Read error: {e}")
            return ROBOT_RESPONSE.unknown_reason
            # return None


class ESA_ROBOT_API:

    def __init__(self, ip: str, port: int, name: str, retry_interval: float = 5.0):

        self.ip = ip
        # self.port = port
        # self.name = name
        # self.retry_interval = retry_interval
        # self.connected = False
        # self.lock = asyncio.Lock()
        # self.conn = None

        self.connections = {
            "STATUS": RobotSocketConnection(ip, 19204, f"{self.ip}-STATUS"),
            "CTRL": RobotSocketConnection(ip, 19205, f"{self.ip}-CTRL"),
            "NAV": RobotSocketConnection(ip, 19206, f"{self.ip}-NAV"),
            "CONF": RobotSocketConnection(ip, 19207, f"{self.ip}-CONF"),
            "OTHER": RobotSocketConnection(ip, 19210, f"{self.ip}-OTHER"),
        }

    ### Status ####
    async def get_status(self, jsonstring: dict, retry: int = 0):
        try:
            resp = await self.connections["STATUS"].send_request(
                key="nav",
                req_id=REQ_ID,
                msg_type=status.robot_status_all1_req,
                msg=jsonstring,
            )
            return resp
        except Exception as E:
            return False

    ## Navigation ###
    async def navigation(self, jsonstring: dict, retry: int = 0):
        try:
            resp = await self.connections["NAV"].send_request(
                key="nav",
                req_id=REQ_ID,
                msg_type=navigation.robot_task_gotarget_req,
                msg=jsonstring,
            )
            return resp
        except Exception as E:
            return False

    async def pause_navigation(self, jsonstring: dict, retry: int = 0):
        try:
            resp = await self.connections["NAV"].send_request(
                key="nav",
                req_id=REQ_ID,
                msg_type=navigation.robot_task_pause_req,
                msg=jsonstring,
            )
            return resp
        except Exception as E:
            return False

    async def resume_navigation(self, jsonstring: dict, retry: int = 0):
        try:
            resp = await self.connections["NAV"].send_request(
                key="nav",
                req_id=REQ_ID,
                msg_type=navigation.robot_task_resume_req,
                msg=jsonstring,
            )
            return resp
        except Exception as E:
            return False

    async def cancel_navigation(self, jsonstring: dict, retry: int = 0):
        try:
            resp = await self.connections["NAV"].send_request(
                key="nav",
                req_id=REQ_ID,
                msg_type=navigation.robot_task_cancel_req,
                msg=jsonstring,
            )
            return resp
        except Exception as E:
            return False

    async def get_navigation_path(self, jsonstring: dict, retry: int = 0):
        try:
            resp = await self.connections["NAV"].send_request(
                key="nav",
                req_id=REQ_ID,
                msg_type=navigation.robot_task_target_path_req,
                msg=jsonstring,
            )
            return resp
        except Exception as E:
            return False

    ################################################### Control APi ###################################################

    async def confirm_local(self, jsonstring: dict, retry: int = 0):
        try:
            resp = await self.connections["CTRL"].send_request(
                key="ctrl",
                req_id=REQ_ID,
                msg_type=control.robot_control_comfirmloc_req,
                msg=jsonstring,
            )
            return resp
        except Exception as E:
            return False

    async def control_relocation(self, jsonstring: dict, retry: int = 0):
        try:
            resp = await self.connections["CTRL"].send_request(
                key="ctrl",
                req_id=REQ_ID,
                msg_type=control.robot_control_reloc_req,
                msg=jsonstring,
            )
            return resp
        except Exception as E:
            return False

    async def cancel_relocation(self, jsonstring: dict, retry: int = 0):
        try:
            resp = await self.connections["CTRL"].send_request(
                key="ctrl",
                req_id=REQ_ID,
                msg_type=control.robot_control_stop_req,
                msg=jsonstring,
            )
            return resp
        except Exception as E:
            return False


class ESAROBOT(ESA_ROBOT_API):

    def __init__(self, robot_id: str, ip: str):

        self.robot_id = robot_id
        self.ip = ip
        self.status = {}

        self.connections = {
            "STATUS": RobotSocketConnection(ip, 19204, f"{robot_id}-STATUS"),
            "CTRL": RobotSocketConnection(ip, 19205, f"{robot_id}-CTRL"),
            "NAV": RobotSocketConnection(ip, 19206, f"{robot_id}-NAV"),
            "CONF": RobotSocketConnection(ip, 19207, f"{robot_id}-CONF"),
            "OTHER": RobotSocketConnection(ip, 19210, f"{robot_id}-OTHER"),
        }

    async def connect_all(self):
        await asyncio.gather(*(conn.connect() for conn in self.connections.values()))

    async def poll_status_interval(self):

        while self.connections["STATUS"].connected:
            # poll_status = await self.connections["STATUS"].send_request(
            #     "status",
            #     REQ_ID,
            #     1100,
            #     {
            #         "keys": [
            #             "battery_level",
            #             "current_map",
            #             "confidence",
            #             "x",
            #             "y",
            #             "angle",
            #             "current_station",
            #         ],
            #         "return_laser": False,
            #         "return_beams3D": False,
            #     },
            # )
            # print("poll_status::::", poll_status)
            # self.status = poll_status
            await asyncio.sleep(1)

    def get(self, name: str) -> RobotSocketConnection:
        return self.connections[name]
