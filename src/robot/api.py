# seer/multi_port_client.py
import asyncio
import struct
import json
from robot.conf import status, navigation, other, config, control

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


class ROBOT_API:

    def __init__(self, ip, id, env, port_conns):
        self.ip = ip
        self.id = (id,)
        self.env = env
        self.port_conns = port_conns  # key -> port
        self.connections = {}  # key -> (reader, writer)
        self.port_callbacks = {}  # key -> callback
        self.reconnect_interval = 5  # seconds
        self._reconnect_tasks = []
        self.reconnect_locks = {
            key: asyncio.Lock() for key in port_conns
        }  # per-key locks

    async def init_connections(self):
        tasks = [self.connect(key) for key in self.port_conns]
        await asyncio.gather(*tasks)
        self._reconnect_tasks = [
            asyncio.create_task(self._auto_reconnect_loop(key))
            for key in self.port_conns
        ]

    async def connect(self, key):
        port = self.port_conns[key]
        async with self.reconnect_locks[key]:
            try:
                reader, writer = await asyncio.open_connection(self.ip, port)
                self.connections[key] = (reader, writer)
                print(f"[Port {port} - {key}] ✅ Connected")
                return reader, writer
            except Exception as e:
                print(f"[Port {port} - {key}] ❌ Connect failed: {e}")
                self.connections[key] = (None, None)
                return None, None

    async def ensure_connection(self, key):
        reader_writer = self.connections.get(key)
        if (
            not reader_writer
            or reader_writer[1] is None
            or reader_writer[1].is_closing()
        ):
            return await self.connect(key)
        return reader_writer

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
        reader, writer = await self.ensure_connection(key)
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
            await self.connect(key)
            return await self.send_request(key, req_id, msg_type, msg, timeout)

        try:
            header = await asyncio.wait_for(reader.readexactly(HEADER_SIZE), timeout)
            m_sync, m_ver, m_serial, m_length, m_type, m_reserved = self.unpack_header(
                header
            )

            if m_length > 0:
                payload = await asyncio.wait_for(reader.readexactly(m_length), timeout)
                response = json.loads(payload.decode("utf-8"))
                if key in self.port_callbacks:
                    await self.port_callbacks[key](
                        action=key, type=msg_type, response=response
                    )
                # return response
                return ROBOT_RESPONSE.success
            return ROBOT_RESPONSE.unknown_reason
            # return None

        except asyncio.TimeoutError:
            print(f"[{key}] ⏱ Timeout waiting for response")
            # return None
            return ROBOT_RESPONSE.resp_time_out
        except asyncio.IncompleteReadError:
            print(f"[{key}] 🔌 Connection closed during read")
            await self.connect(key)
            # return None
            return ROBOT_RESPONSE.read_pack_err
        except Exception as e:
            print(f"[{key}] ❌ Read error: {e}")
            return ROBOT_RESPONSE.unknown_reason
            # return None

    async def _auto_reconnect_loop(self, key):
        while True:
            await asyncio.sleep(self.reconnect_interval)
            reader, writer = self.connections.get(key, (None, None))
            if writer is None or writer.is_closing():
                print(f"[{key}] 🔄 Auto-reconnecting...")
                await self.connect(key)

    def register_callback(self, key, callback):
        self.port_callbacks[key] = callback

    async def on_response(action, type, response):
        print(f"🔔send {action} request [{type}] to robot with response: ", response)

    async def close_all(self):
        for key, (_, writer) in self.connections.items():
            if writer:
                writer.close()
                await writer.wait_closed()
        for task in self._reconnect_tasks:
            task.cancel()

    async def navigation(self, jsonString={}):
        return await self.send_request(
            API_GROUP.navigation,
            REQ_ID,
            navigation.robot_task_gotarget_req,
            jsonString=jsonString,
        )

    async def pause_navigation(self, jsonString={}):
        return await self.send_request(
            API_GROUP.navigation,
            REQ_ID,
            navigation.robot_task_pause_req,
            jsonString=jsonString,
        )

    async def resume_navigation(self, jsonString={}):
        return await self.send_request(
            API_GROUP.navigation,
            REQ_ID,
            navigation.robot_task_resume_req,
            jsonString=jsonString,
        )

    async def cancel_navigation(self, jsonString={}):
        return await self.send_request(
            API_GROUP.navigation,
            REQ_ID,
            navigation.robot_task_cancel_req,
            jsonString=jsonString,
        )


async def main():
    port_conns = {
        "status": 19204,
        "ctrl": 19205,
        "nav": 19206,
        "conf": 19207,
        "other": 19210,
    }

    # client = SimpleSeerClient("127.0.0.1", port_conns)
    # client.register_callback("status", on_response)
    # await client.init_connections()

    # res1 = await client.send_request("status", REQ_ID, 3053, {"id": "AP25"})
    # res2 = await client.send_request("control", REQ_ID, 1005, {})
    # res3 = await client.navigation({"source_id": "SELF_POSITION", "id": "LM1"})

    # print("Response 1:", res1)
    # print("Response 2:", res2)
    # print("Response 3:", res3)

    # await asyncio.sleep(10)
    # await client.close_all()


if __name__ == "__main__":
    asyncio.run(main())
