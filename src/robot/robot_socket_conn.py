import asyncio
import struct
import json
import threading
from src.robot.conf import status, navigation, other, config, control
from src.robot.const.key_store import get_frame_keys
from src.extension.db import robot_statistics
from src.helper.time import seconds_to_hours
import time


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
    "w",
    "battery_level",
    "battery_temp",
    "charging",
    "task_status",
    "target_id",
    "unfinished_path",
    "errors",
    "warnings",
    "notices",
    "fatals",
]

SYNC_ROBOT_EVENT_CONF = {
    "idle": "idle",
    "running": "running",
    "charing": "charing",
    "offline": "offline",
}


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
    async def get_status(self, keys=False, retry: int = 0):
        try:
            resp = await self.connections[API_GROUP.status].send_request(
                key=API_GROUP.status,
                req_id=REQ_ID,
                msg_type=status.robot_status_all1_req,
                msg=keys or self.keys,
            )
            return resp
        except Exception as E:
            return False

    ################################################### Navigation APi ###################################################
    async def navigate(self, jsonstring: dict, retry: int = 0):
        try:
            resp = await self.connections[API_GROUP.navigation].send_request(
                key=API_GROUP.navigation,
                req_id=REQ_ID,
                msg_type=navigation.robot_task_gotarget_req,
                msg=jsonstring,
            )
            return resp
        except Exception as E:
            return False

    async def pause_navigation(self, jsonstring: dict, retry: int = 0):
        try:
            resp = await self.connections[API_GROUP.navigation].send_request(
                key=API_GROUP.navigation,
                req_id=REQ_ID,
                msg_type=navigation.robot_task_pause_req,
                msg=jsonstring,
            )
            return resp
        except Exception as E:
            return False

    async def resume_navigation(self, jsonstring: dict, retry: int = 0):
        try:
            resp = await self.connections[API_GROUP.navigation].send_request(
                key=API_GROUP.navigation,
                req_id=REQ_ID,
                msg_type=navigation.robot_task_resume_req,
                msg=jsonstring,
            )
            return resp
        except Exception as E:
            return False

    async def cancel_navigation(self, jsonstring: dict, retry: int = 0):
        try:
            resp = await self.connections[API_GROUP.navigation].send_request(
                key=API_GROUP.navigation,
                req_id=REQ_ID,
                msg_type=navigation.robot_task_cancel_req,
                msg=jsonstring,
            )
            return resp
        except Exception as E:
            return False

    async def get_navigation_path(self, jsonstring: dict, retry: int = 0):
        try:
            resp = await self.connections[API_GROUP.navigation].send_request(
                key=API_GROUP.navigation,
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

    async def open_loop_ctrl(self, jsonstring: dict, retry: int = 0):
        try:
            resp = await self.connections[API_GROUP.control].send_request(
                key=API_GROUP.control,
                req_id=REQ_ID,
                msg_type=control.robot_control_motion_req,
                msg=jsonstring,
            )
            return resp
        except Exception as E:
            return False

    async def stop_loop_ctrl(self, jsonstring: dict, retry: int = 0):
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
        self.sync_stats = None
        self.last_sync = time.time()
        self.last_event_sync = "offline"
        self.last_event_sync_time = 0
        self.recent_action = {"today_time": 0, "today_odo": 0}

    def _getConnectionByName(self, name: str) -> RobotSocketConnection:
        return self.connections[name]

    async def connect_all(self):

        await asyncio.gather(*(conn.connect() for conn in self.connections.values()))
        status_conn = self._getConnectionByName(API_GROUP.status)

        if status_conn.connected:
            self._task = asyncio.create_task(self.get_status_interval())
            robot_stats = await robot_statistics.find_one_by_conditions(
                {"robot_id": robot_statistics.to_object_id(self.id)}
            )
            if not robot_stats:
                await robot_statistics.insert_one(
                    {
                        "robot_id": robot_statistics.to_object_id(self.id),
                        "date": "2025-09-29",
                        "runtime_hours": 0,
                        "distance_traveled": 0,
                        "error_count": 0,
                        "status_distribution": {
                            "running": 0,
                            "idle": 0,
                            "charge": 0,
                        },
                    }
                )

            self.sync_stats = asyncio.create_task(self.sync_statistics_interval())
        else:
            self.status["connected"] = status_conn.connected

        # if status_conn.connected:
        # threading.Thread(target=self.run_async_from_thread, args=(self.id,)).start()

    def stop_task(self):
        if self._task:
            self._task.cancel()
            self._task = None

    async def get_status_interval(self):

        status_conn = self._getConnectionByName(API_GROUP.status)

        while status_conn.connected:
            poll_status = await self.get_status(keys=self.keys)
            self.status["connected"] = status_conn.connected
            self.status = {**self.status, **poll_status}
            await asyncio.sleep(1.5)

    async def sync_statistics_interval(self):
        status_conn = self._getConnectionByName(API_GROUP.status)

        while status_conn.connected:
            # await self.mark_even_to_sync()
            now = time.time()
            delt_run_time = now - self.last_sync

            await asyncio.sleep(1)
            if delt_run_time < 30:
                continue

            statistics = await robot_statistics.find_one_by_conditions(
                {"robot_id": robot_statistics.to_object_id(self.id)}
            )

            if not statistics:
                continue

            poll_status = await self.get_status(
                get_frame_keys(keys=["odo", "today_odo", "time", "total_time"])
            )

            self.recent_action = {
                "today_time": poll_status["time"],
                "today_odo": poll_status["today_odo"],
            }

            await robot_statistics.update_one(
                filter={"robot_id": robot_statistics.to_object_id(self.id)},
                update={
                    "runtime_hours": seconds_to_hours(poll_status["total_time"] / 1000),
                    "distance_traveled": poll_status["odo"],
                    "error_count": 0,
                },
            )
            self.last_sync = now

        if not status_conn.connected:
            await asyncio.sleep(60)
            return self.sync_statistics_interval()

    async def mark_even_to_sync(self):

        try:
            task_status = self.status.get("task_status", None)
            charging = self.status.get("charging", None)
        except Exception as E:
            pass

        if charging == True:
            print("sync time charing")
            now = time.time()
            if self.last_event_sync != "charging":
                print("mark charging")
                self.last_event_sync = "charging"
                self.last_event_sync_time = now
        else:
            print("sync time")

            now = time.time()

            if self.last_event_sync == "charging":
                delt_charing = (
                    self.last_event_sync_time > 0
                    and now - self.last_event_sync_time
                    or 0
                )
                await robot_statistics.update_one_v2(
                    {"robot_id": robot_statistics.to_object_id(self.id)},
                    {
                        "$inc": {
                            "status_distribution.charge": seconds_to_hours(delt_charing)
                        }
                    },
                )

            if task_status == 2 or task_status == 3:
                #### running
                if self.last_event_sync == "idle":
                    delt = (
                        self.last_event_sync_time > 0
                        and now - self.last_event_sync_time
                        or 0
                    )

                    try:
                        await robot_statistics.update_one_v2(
                            {"robot_id": robot_statistics.to_object_id(self.id)},
                            {
                                "$inc": {
                                    "status_distribution.idle": seconds_to_hours(delt)
                                }
                            },
                        )
                    except Exception as E:
                        print("Err update idle", E)

                #### remark
                if self.last_event_sync != "running":
                    self.last_event_sync = "running"
                    self.last_event_sync_time = now

            elif task_status == 4 or task_status == 0:
                #### task done
                if self.last_event_sync == "running":
                    now = time.time()
                    delt = (
                        self.last_event_sync_time > 0
                        and now - self.last_event_sync_time
                        or 0
                    )
                    try:
                        await robot_statistics.update_one_v2(
                            {"robot_id": robot_statistics.to_object_id(self.id)},
                            {
                                "$inc": {
                                    "status_distribution.running": seconds_to_hours(
                                        delt
                                    )
                                }
                            },
                        )
                        print("del running", delt, seconds_to_hours(delt))
                    except Exception as E:
                        print("Err update running", E)

                #### remark
                if self.last_event_sync != "idle":
                    print("remar idle")
                    self.last_event_sync = "idle"
                    self.last_event_sync_time = now
            # else:
            #     ##### idle
            #     now = time.time()
            #     self.last_event_sync = "idle"
            #     delt = now - self.last_event_sync_time
            #     self.last_event_sync_time = now

    # def run_async_from_thread(self, robot_id):
    #     loop = asyncio.new_event_loop()
    #     asyncio.set_event_loop(loop)
    #     loop.run_until_complete(self.get_status_interval())
    #     loop.close()
