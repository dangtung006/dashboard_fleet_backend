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

        # for id in self.robots:

        #     robot_info = self.robots[id]
        #     robot_id = robot_info["id"]
        #     ip = robot_info["robot_ip"]
        #     self.robot_connections[robot_id] = ESAROBOT(robot_id, ip, env="production")
        #     await self.robot_connections[robot_id].connect_all()

    def get_conn(self, robot_id, port_name):
        return self.robot_connections[robot_id][port_name]

    async def connect_robot(self, robot_id: str):
        robot: ESAROBOT = self.robots.get(robot_id)
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
        robot_info = list(self.robots.values())
        return robot_info
        robot_data = []

        for robot in robot_info:
            robot_id = robot["id"]
            if robot_id in self.robot_connections:
                robot_conn = self.robot_connections[robot_id]
                robot_data.append({**robot, **robot_conn.status})
        return robot_data

    def get_robot_by_id(self, robot_id: str):
        robot = self.robots.get(robot_id, None)
        if robot_id in self.robot_connections:
            status = self.robot_connections[robot_id].status
            robot = {**robot, **status} if robot else robot
        return robot

    async def ctrl_joystick(self, cmd):
        type = cmd["type"]
        direction = cmd["direction"]
        robot_id = cmd["robot_id"]
        distance = cmd["distance"]

        robot_conn: ESAROBOT = self.robot_connections[robot_id]
        if not robot_conn:
            return False
        vx = (
            0.1
            if direction == "FORWARD"
            else 0 if direction == "LEFT" or direction == "RIGHT" else -0.1
        )

        w = (
            0.1
            if direction == "RIGHT"
            else 0 if direction == "FORWARD" or direction == "BACKWARD" else -0.1
        )

        orderByCmd = {
            "vx": vx,
            "vy": 0,
            "w": w,
            "duration": 0,
        }

        if type == "move":
            resp = await robot_conn.open_loop_ctrl(jsonstring=orderByCmd)
            return resp

        elif type == "stop":
            resp = await robot_conn.stop_loop_ctrl(jsonstring={})
            return resp

    async def stop_ctrl_joystick(self, cmd):
        robot_id = cmd["robot_id"]
        robot_conn: ESAROBOT = self.robot_connections[robot_id]
        if not robot_conn:
            return

        resp = await robot_conn.stop_loop_ctrl(jsonstring={})
        return resp

    async def go_target(self, robot_id, target):
        robot_conn: ESAROBOT = self.robot_connections[robot_id]
        if not robot_conn:
            return False

        resp = await robot_conn.navigate(
            jsonstring={"source_id": "SELF_POSITION", "id": target}
        )
        return resp

    def get_robot_status_by_id(self, robot_id: str):
        return self.robot_connections.get(robot_id, None).status

    def get_recent_stats(self):
        try:
            robots = list(self.robot_connections)
            recent_stats = [
                {
                    **self.robots[robot_id],
                    **self.robot_connections[robot_id].recent_action,
                }
                for robot_id in robots
            ]
            return recent_stats
        except Exception as E:
            print(E)
