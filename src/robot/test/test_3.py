import asyncio
import json
import struct


PACK_FMT_STR = "!BBHLH6s"
HEADER_SIZE = struct.calcsize(PACK_FMT_STR)


def build_packet(req_id, msg_type, msg={}):
    json_str = json.dumps(msg)
    msg_len = len(json_str) if msg else 0
    header = struct.pack(
        PACK_FMT_STR,
        0x5A,  # Sync
        0x01,  # Version
        req_id,
        msg_len,
        msg_type,
        b"\x00" * 6,  # Reserved
    )
    print(
        "{:02X} {:02X} {:04X} {:08X} {:04X}".format(
            0x5A, 0x01, req_id, msg_len, msg_type
        )
    )
    if msg:
        header += json_str.encode("ascii")
        print(msg)
    return header


def unpack_header(data):
    return struct.unpack(PACK_FMT_STR, data)


class SeerTCPFramer:
    def __init__(self, reader: asyncio.StreamReader):
        self.reader = reader

    async def read_packet(self, timeout: float = 5.0):
        """Đọc 1 gói tin SEER hoàn chỉnh (header + payload)"""
        try:
            # 1️⃣ Đọc header
            header_data = await asyncio.wait_for(
                self.reader.readexactly(HEADER_SIZE), timeout
            )

            m_sync, m_ver, m_serial, m_length, m_type, m_reserved = unpack_header(
                header_data
            )

            header_dict = {
                "sync": m_sync,
                "version": m_ver,
                "serial": m_serial,
                "length": m_length,
                "type": m_type,
                "reserved": m_reserved,
            }

            # 2️⃣ Đọc JSON payload
            payload = b""
            if m_length > 0:
                payload = await asyncio.wait_for(
                    self.reader.readexactly(m_length), timeout
                )
                try:
                    json_data = json.loads(payload.decode("utf-8"))
                except json.JSONDecodeError as e:
                    print(f"[Framer] ❌ JSON decode error: {e}")
                    json_data = None
            else:
                json_data = None

            return {
                "header": header_dict,
                "json": json_data,
                "raw": header_data + payload,
            }

        except asyncio.TimeoutError:
            print("[Framer] ⏰ Timeout while reading packet")
            return None
        except Exception as e:
            print(f"[Framer] ❌ Unexpected error: {e}")
            return None


class SeerTCPClient:
    def __init__(self, robot_ip: str):
        self.robot_ip = robot_ip
        self.connections = {}  # {port: (reader, writer)}
        self.reconnect_interval = 3  # seconds

    async def connect_port(self, port: int):
        while True:
            try:
                reader, writer = await asyncio.open_connection(self.robot_ip, port)
                self.connections[port] = (reader, writer)
                print(f"[{port}] ✅ Connected to robot {self.robot_ip}")
                return
            except Exception as e:
                print(f"[{port}] 🔁 Reconnect failed: {e}")
                await asyncio.sleep(self.reconnect_interval)

    async def ensure_connected(self, port: int):
        if port not in self.connections or self.connections[port][1].is_closing():
            await self.connect_port(port)

    async def send_packet(self, port: int, packet: bytes):
        await self.ensure_connected(port)
        reader, writer = self.connections[port]
        try:
            writer.write(packet)
            await writer.drain()
        except (BrokenPipeError, ConnectionResetError) as e:
            print(f"[{port}] 🔌 Writer closed: {e}, reconnecting...")
            await self.connect_port(port)
            await self.send_packet(port, packet)

    async def receive_packet(self, port: int):
        await self.ensure_connected(port)
        reader, _ = self.connections[port]
        try:
            framer = SeerTCPFramer(reader)
            return await framer.read_packet()
        except (asyncio.IncompleteReadError, ConnectionResetError) as e:
            print(f"[{port}] 🔄 Read error: {e}, reconnecting...")
            await self.connect_port(port)
            return None

    async def close_all(self):
        for port, (_, writer) in self.connections.items():
            writer.close()
            await writer.wait_closed()


async def main():
    client = SeerTCPClient("192.168.1.100")
    # Gửi liên tục → nếu robot restart thì client sẽ reconnect
    while True:
        packet = build_packet(1, 0x0456, {"task_ids": ["SEER78914"]})
        await client.send_packet(19204, packet)
        response = await client.receive_packet(19204)
        print("📬 Received:", response)
        await asyncio.sleep(5)
