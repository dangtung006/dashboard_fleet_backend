import asyncio
import struct
import json
import threading
from src.robot.conf import status, navigation, other, config, control
from src.robot.const.key_store import get_frame_keys

PACK_FMT_STR = "!BBHLH6s"
HEADER_SIZE = struct.calcsize(PACK_FMT_STR)
REQ_ID = 1

KEY_CONF = [
    "blocked",
    "emergency",
    "reloc_status",
    "area_ids",
    "x",
    "y",
    "angle",
    "confidence",
    "current_station",
    "vx",
    "vy",
    "battery_level",
    "charging",
    "task_status",
    "target_id",
    "unfinished_path",
    "errors",
    "warnings",
    "notices",
    "fatals",
]


class API_GROUP:
    navigation = "nav"
    status = "status"
    control = "ctrl"
    config = "conf"
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

        # while not self.connected:
        #     try:
        #         reader, writer = await asyncio.open_connection(self.ip, self.port)
        #         # asyncio.timeout(3)
        #         self.connected = True
        #         print(f"[{self.name}] Connected to {self.ip}:{self.port}")
        #         self.conn = (reader, writer)
        #     except Exception as e:
        #         print(
        #             f"[{self.name}] Failed to connect: {e}. Retrying in {self.retry_interval}s"
        #         )
        #         # await asyncio.sleep(self.retry_interval)

        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.ip, self.port), timeout=3
            )
            print(f"✅ Kết nối thành công {self.ip}:{self.port}")
            self.connected = True
            # return reader, writer
            self.conn = (reader, writer)
        except asyncio.TimeoutError:
            print(f"⏳ Timeout sau {3}s, huỷ kết nối tới robot {self.ip}- {self.name}")
            # await self.close_conn()
            # return None, None
        except Exception as e:
            print(f"❌ Lỗi khi kết nối: {e}")
            # await self.close_conn()
            # return None, None

    async def close_conn(self):
        reader, writer = self.conn
        if writer:
            writer.close()
            await writer.wait_closed()

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

    def __init__(
        self, ip: str, id: str, keys: str, env: str, retry_interval: float = 5.0
    ):

        self.ip = ip
        self.id = id
        self.keys = keys
        self.env = env
        self.retry_interval = retry_interval

        self.connections = {
            API_GROUP.status: RobotSocketConnection(ip, 19204, f"{self.ip}-STATUS"),
            API_GROUP.control: RobotSocketConnection(ip, 19205, f"{self.ip}-CTRL"),
            API_GROUP.navigation: RobotSocketConnection(ip, 19206, f"{self.ip}-NAV"),
            API_GROUP.config: RobotSocketConnection(ip, 19207, f"{self.ip}-CONF"),
            API_GROUP.other: RobotSocketConnection(ip, 19210, f"{self.ip}-OTHER"),
        }

    ################################################### Status APi ###################################################
    async def get_status(self, retry: int = 0):
        try:
            resp = await self.connections[API_GROUP.status].send_request(
                key=API_GROUP.status,
                req_id=REQ_ID,
                msg_type=status.robot_status_all1_req,
                msg=self.keys,
            )
            return resp
        except Exception as E:
            return False

    ################################################### Navigation APi ###################################################
    async def navigate(self, jsonstring: dict, retry: int = 0):
        try:
            resp = await self.connections[API_GROUP.status].send_request(
                key=API_GROUP.status,
                req_id=REQ_ID,
                msg_type=navigation.robot_task_gotarget_req,
                msg=jsonstring,
            )
            return resp
        except Exception as E:
            return False

    async def pause_navigation(self, jsonstring: dict, retry: int = 0):
        try:
            resp = await self.connections[API_GROUP.status].send_request(
                key=API_GROUP.status,
                req_id=REQ_ID,
                msg_type=navigation.robot_task_pause_req,
                msg=jsonstring,
            )
            return resp
        except Exception as E:
            return False

    async def resume_navigation(self, jsonstring: dict, retry: int = 0):
        try:
            resp = await self.connections[API_GROUP.status].send_request(
                key=API_GROUP.status,
                req_id=REQ_ID,
                msg_type=navigation.robot_task_resume_req,
                msg=jsonstring,
            )
            return resp
        except Exception as E:
            return False

    async def cancel_navigation(self, jsonstring: dict, retry: int = 0):
        try:
            resp = await self.connections[API_GROUP.status].send_request(
                key=API_GROUP.status,
                req_id=REQ_ID,
                msg_type=navigation.robot_task_cancel_req,
                msg=jsonstring,
            )
            return resp
        except Exception as E:
            return False

    async def get_navigation_path(self, jsonstring: dict, retry: int = 0):
        try:
            resp = await self.connections[API_GROUP.status].send_request(
                key=API_GROUP.status,
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
            resp = await self.connections[API_GROUP.control].send_request(
                key=API_GROUP.control,
                req_id=REQ_ID,
                msg_type=control.robot_control_comfirmloc_req,
                msg=jsonstring,
            )
            return resp
        except Exception as E:
            return False

    async def control_relocation(self, jsonstring: dict, retry: int = 0):
        try:
            resp = await self.connections[API_GROUP.control].send_request(
                key=API_GROUP.control,
                req_id=REQ_ID,
                msg_type=control.robot_control_reloc_req,
                msg=jsonstring,
            )
            return resp
        except Exception as E:
            return False

    async def cancel_relocation(self, jsonstring: dict, retry: int = 0):
        try:
            resp = await self.connections[API_GROUP.control].send_request(
                key=API_GROUP.control,
                req_id=REQ_ID,
                msg_type=control.robot_control_stop_req,
                msg=jsonstring,
            )
            return resp
        except Exception as E:
            return False

    ################################################### Config APi ###################################################

    async def device_set_shelf(self, jsonstring: dict, retry: int = 0):
        try:
            resp = await self.connections[API_GROUP.config].send_request(
                key=API_GROUP.config,
                req_id=REQ_ID,
                msg_type=config.robot_config_set_shelfshape_req,
                msg=jsonstring,
            )
            return resp
        except Exception as E:
            return False

    async def device_unset_shelf(self, jsonstring: dict, retry: int = 0):
        try:
            resp = await self.connections[API_GROUP.config].send_request(
                key=API_GROUP.config,
                req_id=REQ_ID,
                msg_type=config.robot_config_clear_goodsshape_req,
                msg=jsonstring,
            )
            return resp
        except Exception as E:
            return False

    async def preempt_control(self, jsonstring: dict, retry: int = 0):
        try:
            resp = await self.connections[API_GROUP.config].send_request(
                key=API_GROUP.config,
                req_id=REQ_ID,
                msg_type=config.robot_config_lock_req,
                msg=jsonstring,
            )
            return resp
        except Exception as E:
            return False

    async def realse_control(self, jsonstring: dict, retry: int = 0):
        try:
            resp = await self.connections[API_GROUP.config].send_request(
                key=API_GROUP.config,
                req_id=REQ_ID,
                msg_type=config.robot_config_unlock_req,
                msg=jsonstring,
            )
            return resp
        except Exception as E:
            return False

    async def clear_all_errors(self, jsonstring: dict, retry: int = 0):
        try:
            resp = await self.connections[API_GROUP.config].send_request(
                key=API_GROUP.config,
                req_id=REQ_ID,
                msg_type=config.robot_config_clearallerrors_req,
                msg=jsonstring,
            )
            return resp
        except Exception as E:
            return False

    ################################################### Other APi ###################################################

    async def load_jack(self, jsonstring: dict, retry: int = 0):
        try:
            resp = await self.connections[API_GROUP.other].send_request(
                key=API_GROUP.other,
                req_id=REQ_ID,
                msg_type=other.robot_other_jack_load_req,
                msg=jsonstring,
            )
            return resp
        except Exception as E:
            return False

    async def unload_jack(self, jsonstring: dict, retry: int = 0):
        try:
            resp = await self.connections[API_GROUP.other].send_request(
                key=API_GROUP.other,
                req_id=REQ_ID,
                msg_type=other.robot_other_jack_unload_req,
                msg=jsonstring,
            )
            return resp
        except Exception as E:
            return False

    async def set_jack_height(self, jsonstring: dict, retry: int = 0):
        try:
            resp = await self.connections[API_GROUP.other].send_request(
                key=API_GROUP.other,
                req_id=REQ_ID,
                msg_type=other.robot_other_jack_set_height_req,
                msg=jsonstring,
            )
            return resp
        except Exception as E:
            return False

    async def jack_stop(self, jsonstring: dict, retry: int = 0):
        try:
            resp = await self.connections[API_GROUP.other].send_request(
                key=API_GROUP.other,
                req_id=REQ_ID,
                msg_type=other.robot_other_jack_stop_req,
                msg=jsonstring,
            )
            return resp
        except Exception as E:
            return False


class ESAROBOT(ESA_ROBOT_API):

    def __init__(self, robot_id: str, ip: str, env: str):

        super().__init__(ip=ip, id=robot_id, keys=get_frame_keys(KEY_CONF), env=env)
        self.status = {}
        self._task = None

    def _getConnectionByName(self, name: str) -> RobotSocketConnection:
        return self.connections[name]

    async def connect_all(self):

        await asyncio.gather(*(conn.connect() for conn in self.connections.values()))
        status_conn = self._getConnectionByName(API_GROUP.status)

        if status_conn.connected:
            self._task = asyncio.create_task(self.get_status_interval())
        # if status_conn.connected:
        # threading.Thread(target=self.run_async_from_thread, args=(self.id,)).start()

    def stop_task(self):
        if self._task:
            self._task.cancel()
            self._task = None

    async def get_status_interval(self):

        status_conn = self._getConnectionByName(API_GROUP.status)

        while status_conn.connected:
            poll_status = await self.get_status()
            print("poll_status:::::", poll_status)
            self.status = poll_status
            await asyncio.sleep(1.5)

    # def run_async_from_thread(self, robot_id):
    #     loop = asyncio.new_event_loop()
    #     asyncio.set_event_loop(loop)
    #     loop.run_until_complete(self.get_status_interval())
    #     loop.close()
