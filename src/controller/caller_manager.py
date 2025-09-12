import socket, asyncio, errno, time
from src.extension.db import callers


class CallerManager:

    def __init__(self):
        self.callers: dict = {}

    async def init_from_config(self):
        resp = await callers.find_all()
        print("Loading robot configurations from DB...", resp)
        # robot_configs = []

        async for doc in resp:
            self.callers[str(doc["_id"])] = callers.serialize(doc)
        print("Initialized RobotManager with robots:", self.callers)

    async def connect_robot(self, robot_id: str):
        robot = self.callers.get(robot_id)
        if robot:
            await robot.connect_all()
        else:
            print(f"Robot {robot_id} not found")

    def get_caller(self, robot_id: str):
        return self.callers.get(robot_id)

    async def save_caller(self, data: dict):

        # try:
        #     robot_id = data["id"]
        #     # data = robots.serialize(data)
        # except Exception as e:
        #     print(f"Error serializing data: {e}")
        #     return
        robot_id = data["id"]
        if robot_id in self.callers:
            await callers.update_one({"id": robot_id}, {"$set": data})
            self.callers[robot_id].update(data)
        else:
            await callers.insert_one(data)
            self.callers[robot_id] = data

        return self.callers[robot_id]

        # connections = RobotSession(robot_id, data["ip"])
        # self.robot_connections[robot_id] = connections
        # self.robots[robot_id] = connections

    async def add_caller(self, robot: dict):
        resp = await callers.insert_one(robot)
        print("Insert response:", resp)
        print("Insert inserted_id:", resp.inserted_id)
        inserted_id = str(resp.inserted_id)
        print("Insert inserted_id:", inserted_id)
        if not inserted_id:
            return None
        else:
            added_robot = await callers.find_by_id(inserted_id)
            # self.robots[inserted_id].update(robots.serialize(updated_robot))
            self.callers[inserted_id] = callers.serialize(added_robot)
            return self.callers[inserted_id]

    async def update_caller(self, robot_id: str, robot: dict):
        print("Updating robot:", callers.to_object_id(robot_id))
        resp = await callers.update_one({"_id": callers.to_object_id(robot_id)}, robot)

        # resp = await robots.update_by_id(robot_id, {"$set": robot})

        if resp.modified_count > 0:
            updated_robot = await callers.find_by_id(robot_id)
            self.callers[robot_id].update(callers.serialize(updated_robot))
            return self.callers[robot_id]

        return {"status": "failed", "message": "No document updated"}

        # if robot_id in self.robots:
        #     self.robots[robot_id].update(connections)
        # else:
        #     self.robots[robot_id] = connections

    async def remove_caller(self, robot_id: str):
        resp = await callers.delete_by_id(callers.to_object_id(robot_id))
        print("Delete response:", resp.deleted_count)

        if resp.deleted_count > 0:
            print("robot_id in self.robots", robot_id in self.callers)
            if robot_id in self.callers:
                del self.callers[robot_id]
            return {"status": "success", "message": "Robot deleted"}
        # if robot_id in self.robots:
        #     del self.robots[robot_id]

    def get_all_caller(self):
        try:
            callers = list(self.callers.values()) if len(self.callers) > 0 else []
            return callers
        except Exception as e:
            print("Error getting caller count:", e)
            return []

    def get_caller_by_id(self, robot_id: str):
        return self.callers.get(robot_id, None)

    # async def connect_all(self):
    #     await asyncio.gather(*(robot.connect_all() for robot in self.robots.values()))
