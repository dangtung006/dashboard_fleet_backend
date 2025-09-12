import socket, asyncio, errno, time
from src.extension.db import robots

ROBOTS = [
    {
        "id": "robot_001",
        "ip": "127.0.0.1",
        "ports": {"STATUS": 19204, "CTRL": 19205, "NAV": 19206},
    },
    {
        "id": "robot_002",
        "ip": "127.0.0.1",
        "ports": {"STATUS": 19304, "CTRL": 19305, "NAV": 19306},
    },
]


class SocketConnection:
    def __init__(self, name: str, ip: str, port: int):
        self.name = name
        self.ip = ip
        self.port = port
        self.sock = None
        self.connected = False

    async def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(False)
        try:
            await asyncio.get_running_loop().sock_connect(
                self.sock, (self.ip, self.port)
            )
            self.connected = True
            print(f"[{self.name}] Connected to robot at {self.ip}:{self.port}")
        except Exception as e:
            self.connected = False
            print(f"[{self.name}] Connection failed: {e}")


class SocketConnection:
    ...

    def is_socket_valid(self) -> bool:
        return self.sock is not None and self.sock.fileno() != -1

    async def safe_send(self, data: str):
        if not self.is_socket_valid():
            print(f"[{self.name}] Invalid socket, reconnecting...")
            await self.connect()
        try:
            await asyncio.get_running_loop().sock_sendall(self.sock, data.encode())
        except (OSError, ConnectionResetError) as e:
            print(f"[{self.name}] Send error: {e}, reconnecting...")
            self.connected = False
            self.sock.close()
            await self.connect()

    async def safe_recv(self, nbytes: int = 1024) -> str:
        if not self.is_socket_valid():
            print(f"[{self.name}] Invalid socket, reconnecting...")
            await self.connect()
        try:
            data = await asyncio.get_running_loop().sock_recv(self.sock, nbytes)
            return data.decode()
        except (OSError, ConnectionResetError) as e:
            print(f"[{self.name}] Receive error: {e}, reconnecting...")
            self.connected = False
            self.sock.close()
            await self.connect()
            return ""


class SocketConnection:
    def __init__(self, robot_id: str, name: str, ip: str, port: int):
        self.robot_id = robot_id
        self.name = name
        self.ip = ip
        self.port = port
        self.sock = None
        self.connected = False

    async def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setblocking(False)
            await asyncio.get_running_loop().sock_connect(
                self.sock, (self.ip, self.port)
            )
            self.connected = True
            print(f"[{self.robot_id} - {self.name}] ✅ Connected")
        except Exception as e:
            self.connected = False
            print(f"[{self.robot_id} - {self.name}] ❌ Connect failed: {e}")

    def is_alive(self):
        return self.sock and self.sock.fileno() != -1


class SocketConnection:
    def __init__(self, ip: str, port: int, name: str, retry_interval: float = 5.0):
        self.ip = ip
        self.port = port
        self.name = name
        self.retry_interval = retry_interval
        self.sock = None
        self.connected = False
        self.lock = asyncio.Lock()

    async def connect(self):
        while not self.connected:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.setblocking(False)
                await asyncio.get_running_loop().sock_connect(
                    self.sock, (self.ip, self.port)
                )
                self.connected = True
                print(f"[{self.name}] Connected to {self.ip}:{self.port}")
            except Exception as e:
                print(
                    f"[{self.name}] Failed to connect: {e}. Retrying in {self.retry_interval}s"
                )
                await asyncio.sleep(self.retry_interval)

    async def send(self, data: str):
        async with self.lock:
            if not self.connected:
                await self.connect()
            try:
                await asyncio.get_running_loop().sock_sendall(self.sock, data.encode())
            except Exception as e:
                print(f"[{self.name}] Send failed: {e}")
                self.connected = False
                await self.connect()

    async def recv(self, nbytes: int = 1024) -> str:
        async with self.lock:
            if not self.connected:
                await self.connect()
            try:
                data = await asyncio.get_running_loop().sock_recv(self.sock, nbytes)
                return data.decode()
            except Exception as e:
                print(f"[{self.name}] Receive failed: {e}")
                self.connected = False
                await self.connect()
                return ""


class RobotSession:

    def __init__(self, robot_id: str, ip: str):
        self.robot_id = robot_id
        self.ip = ip
        self.connections = {
            "STATUS": SocketConnection(ip, 19204, f"{robot_id}-STATUS"),
            "CTRL": SocketConnection(ip, 19205, f"{robot_id}-CTRL"),
            "NAV": SocketConnection(ip, 19206, f"{robot_id}-NAV"),
            "CONF": SocketConnection(ip, 19207, f"{robot_id}-CONF"),
            "OTHER": SocketConnection(ip, 19210, f"{robot_id}-OTHER"),
        }

    async def connect_all(self):
        await asyncio.gather(*(conn.connect() for conn in self.connections.values()))

    def get(self, name: str) -> SocketConnection:
        return self.connections[name]


class RobotManager:

    def __init__(self):
        self.robot_connections: dict[str, RobotSession] = {}
        self.robots: dict = {}

    async def init_from_config(self):
        resp = await robots.find_all()
        print("Loading robot configurations from DB...", resp)
        # robot_configs = []

        async for doc in resp:
            self.robots[str(doc["_id"])] = robots.serialize(doc)
        print("Initialized RobotManager with robots:", self.robots)
        # doc["_id"] = str(doc["_id"])
        # doc["created_at"] = doc["created_at"].isoformat()
        # doc["updated_at"] = doc["updated_at"].isoformat()
        # robot_configs.append(robots.serialize(doc))
        # print("Initializing RobotManager with configs from DB...", robot_configs)
        # self.robots = robots.serialize(robot_configs)

        # async for config in robot_configs:
        #     robot_id = config["id"]
        #     ip = config["ip"]
        #     self.robot_connections[robot_id] = RobotSession(robot_id, ip)

        # await self.robots[robot_id].connect_all()

        # for r in config:
        #     conns = {}
        #     for name, port in r["ports"].items():
        #         conn = SocketConnection(r["id"], name, r["ip"], port)
        #         await conn.connect()
        #         conns[name] = conn
        #     self.robots[r["id"]] = conns

    # def get_conn(self, robot_id, port_name):
    #     return self.robots[robot_id][port_name]

    async def connect_robot(self, robot_id: str):
        robot = self.robots.get(robot_id)
        if robot:
            await robot.connect_all()
        else:
            print(f"Robot {robot_id} not found")

    def get_robot(self, robot_id: str):
        return self.robots.get(robot_id)

    async def save_robot(self, data: dict):

        # try:
        #     robot_id = data["id"]
        #     # data = robots.serialize(data)
        # except Exception as e:
        #     print(f"Error serializing data: {e}")
        #     return
        robot_id = data["id"]
        if robot_id in self.robots:
            await robots.update_one({"id": robot_id}, {"$set": data})
            self.robots[robot_id].update(data)
        else:
            await robots.insert_one(data)
            self.robots[robot_id] = data

        return self.robots[robot_id]

        # connections = RobotSession(robot_id, data["ip"])
        # self.robot_connections[robot_id] = connections
        # self.robots[robot_id] = connections

    async def add_robot(self, robot: dict):
        resp = await robots.insert_one(robot)
        print("Insert response:", resp)
        print("Insert inserted_id:", resp.inserted_id)
        inserted_id = str(resp.inserted_id)
        print("Insert inserted_id:", inserted_id)
        if not inserted_id:
            return None
        else:
            added_robot = await robots.find_by_id(inserted_id)
            # self.robots[inserted_id].update(robots.serialize(updated_robot))
            self.robots[inserted_id] = robots.serialize(added_robot)
            return self.robots[inserted_id]

    async def update_robot(self, robot_id: str, robot: dict):
        print("Updating robot:", robots.to_object_id(robot_id))
        resp = await robots.update_one({"_id": robots.to_object_id(robot_id)}, robot)

        # resp = await robots.update_by_id(robot_id, {"$set": robot})

        if resp.modified_count > 0:
            updated_robot = await robots.find_by_id(robot_id)
            self.robots[robot_id].update(robots.serialize(updated_robot))
            return self.robots[robot_id]

        return {"status": "failed", "message": "No document updated"}

        # if robot_id in self.robots:
        #     self.robots[robot_id].update(connections)
        # else:
        #     self.robots[robot_id] = connections

    async def remove_robot(self, robot_id: str):
        resp = await robots.delete_by_id(robots.to_object_id(robot_id))
        print("Delete response:", resp.deleted_count)

        if resp.deleted_count > 0:
            print("robot_id in self.robots", robot_id in self.robots)
            if robot_id in self.robots:
                del self.robots[robot_id]
            return {"status": "success", "message": "Robot deleted"}
        # if robot_id in self.robots:
        #     del self.robots[robot_id]

    def get_all_robots(self):
        return list(self.robots.values())
        # for conn in self.robot_connections.values():
        #     print(conn.robot_id, conn.ip)

        # return self.robots

    def get_robot_by_id(self, robot_id: str):
        return self.robots.get(robot_id, None)

    # async def connect_all(self):
    #     await asyncio.gather(*(robot.connect_all() for robot in self.robots.values()))
