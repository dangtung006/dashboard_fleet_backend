import socket, asyncio, errno, time
from src.extension.db import callers


class CallerManager:

    def __init__(self):
        self.callers: dict = {}

    async def init_from_config(self):
        # resp = await callers.find_all()
        # async for doc in resp:
        #     self.callers[str(doc["_id"])] = callers.serialize(doc)
        pass

    async def connect_caller(self, caller_id: str):
        # robot = self.callers.get(robot_id)
        # if robot:
        #     await robot.connect_all()
        # else:
        #     print(f"Robot {robot_id} not found")
        pass

    async def disconnect_caller(self, caller_id: str):
        # robot = self.callers.get(robot_id)
        # if robot:
        #     await robot.disconnect_all()
        # else:
        #     print(f"Robot {robot_id} not found")
        pass

    def get_connected_caller_by_id(self, caller_id: str):
        return self.callers.get(caller_id, None)

    def get_connected_callers(self):
        try:
            callers = list(self.callers.values()) if len(self.callers) > 0 else []
            return callers
        except Exception as e:
            print("Error getting caller count:", e)
            return []

    ############################################## Caller Management #############################################

    async def save_caller(self, data: dict):
        robot_id = data["id"]
        if robot_id in self.callers:
            await callers.update_one({"id": robot_id}, {"$set": data})
            self.callers[robot_id].update(data)
        else:
            await callers.insert_one(data)
            self.callers[robot_id] = data

        return self.callers[robot_id]

    async def add_caller(self, caller: dict):
        resp = await callers.insert_one(caller)
        inserted_id = str(resp.inserted_id)
        if not inserted_id:
            return None
        else:
            added_robot = await callers.find_by_id(inserted_id)
            # self.robots[inserted_id].update(robots.serialize(updated_robot))
            self.callers[inserted_id] = callers.serialize(added_robot)
            return self.callers[inserted_id]

    async def update_caller(self, caller_id: str, caller: dict):

        resp = await callers.update_one(
            {"_id": callers.to_object_id(caller_id)}, caller
        )

        # if resp.modified_count > 0:
        #     updated_robot = await callers.find_by_id(caller_id)
        #     self.callers[caller_id].update(callers.serialize(updated_robot))
        #     return self.callers[caller_id]

        return True

    async def remove_caller(self, robot_id: str):
        resp = await callers.delete_by_id(callers.to_object_id(robot_id))

        # if resp.deleted_count > 0:
        #     print("robot_id in self.robots", robot_id in self.callers)
        #     if robot_id in self.callers:
        #         del self.callers[robot_id]
        #     return {"status": "success", "message": "Robot deleted"}
        return True

    async def get_caller_list(self):
        try:
            resp = await callers.find_list(page=1, page_size=10)
            return [callers.serialize(doc) for doc in resp]

        except Exception as e:
            print("Error getting caller count:", e)
            return []

    async def get_caller_by_id(self, caller_id: str):
        try:
            resp = await callers.find_by_id(id=caller_id)
            return callers.serialize(resp) if resp else None

        except Exception as e:
            print("Error getting caller count:", e)
            return None
