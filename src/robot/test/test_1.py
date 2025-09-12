import asyncio
import struct
import json

IP = "192.168.1.100"
PORT = 19204


async def send_and_receive(req_id, msg_type, payload):
    try:
        reader, writer = await asyncio.open_connection(IP, PORT)

        # Build packet
        data_str = json.dumps(payload)
        length = len(data_str)
        header = struct.pack(
            "!BBHLH6s", 0x5A, 0x01, req_id, length, msg_type, b"\x00" * 6
        )
        packet = header + data_str.encode()

        writer.write(packet)
        await writer.drain()

        # Receive
        try:
            header = await asyncio.wait_for(reader.readexactly(16), timeout=5)
            _, _, serial, length, _, _ = struct.unpack("!BBHLH6s", header)
            json_data = await asyncio.wait_for(reader.readexactly(length), timeout=5)
            print("✅ Received:", json.loads(json_data))
        except asyncio.TimeoutError:
            print("⏱ Timeout waiting for response.")
        except asyncio.IncompleteReadError:
            print("📴 Connection lost mid-read.")
        finally:
            writer.close()
            await writer.wait_closed()

    except (ConnectionResetError, BrokenPipeError, OSError) as e:
        print(f"🔌 Connection error: {e}. Retrying...")
        await asyncio.sleep(1)
        await send_and_receive(req_id, msg_type, payload)


async def main():
    res = await send_and_receive(
        port=19204, req_id=1, msg_type=0x0456, msg={"task_ids": ["SEER001"]}
    )
    print(res)


asyncio.run(main())
