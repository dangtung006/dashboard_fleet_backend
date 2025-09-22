from src.extension.db import robots
import asyncio
import threading
from src.robot.robot_socket_conn import ESAROBOT


class RobotManager:

    def __init__(self):
        self.robot_connections: dict[str, ESAROBOT] = {}
        self.robots: dict = {}

    async def init_connections_from_config(self):

        resp = await robots.find_all()

        async for doc in resp:
            self.robots[str(doc["_id"])] = robots.serialize(doc)

        for id in self.robots:

            robot_info = self.robots[id]
            robot_id = robot_info["_id"]
            ip = robot_info["robot_ip"]

            print("robot_id:::", robot_id)
            print("ip:::", ip)
            self.robot_connections[robot_id] = ESAROBOT(robot_id, ip, env="production")
            await self.robot_connections[robot_id].connect_all()

            threading.Thread(
                target=self.run_async_from_thread, args=(robot_id,)
            ).start()

    def get_conn(self, robot_id, port_name):
        return self.robot_connections[robot_id][port_name]

    def run_async_from_thread(self, robot_id):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.robot_connections[robot_id].get_status_interval())
        loop.close()

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

    def get_robot_status_by_id(self, robot_id: str):
        return self.robot_connections.get(robot_id, None).status

    # async def connect_all(self):
    #     await asyncio.gather(*(robot.connect_all() for robot in self.robots.values()))
