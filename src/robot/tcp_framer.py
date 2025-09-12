import asyncio
import json
import struct

PACK_FMT_STR = "!BBHLH6s"
HEADER_SIZE = struct.calcsize(PACK_FMT_STR)


class RobotTCPFramer:
    def __init__(self, reader: asyncio.StreamReader):
        self.reader = reader

    async def read_packet(self, timeout: float = 5.0):
        """Đọc 1 gói tin Robot hoàn chỉnh (header + payload)"""
        try:
            # 1️⃣ Đọc header
            header_data = await asyncio.wait_for(
                self.reader.readexactly(HEADER_SIZE), timeout
            )
            header = struct.unpack(PACK_FMT_STR, header_data)

            m_sync, m_ver, m_serial, m_length, m_type, m_reserved = header
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
