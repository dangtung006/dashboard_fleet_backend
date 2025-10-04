from src.extension.db import charing_stations as charing_collections
from src.dto.charing_station import CharingStationInDB


class CharingStationManager:

    def __init__(self):
        self.charing_stations: dict = {}

    async def init_from_config(self):
        # resp = await charing_stations.find_all()
        # async for doc in resp:
        #     self.charing_stations[str(doc["_id"])] = charing_stations.serialize(doc)
        pass

    async def connect_charing_st(self, charing_st_id: str):
        # robot = self.charing_stations.get(robot_id)
        # if robot:
        #     await robot.connect_all()
        # else:
        #     print(f"Robot {robot_id} not found")
        pass

    async def disconnect_charing_st(self, charing_st_id: str):
        # robot = self.charing_stations.get(robot_id)
        # if robot:
        #     await charing_stations.disconnect_all()
        # else:
        #     print(f"Robot {robot_id} not found")
        pass

    def get_connected_charing_st_by_id(self, charing_st_id: str):
        return self.charing_stations.get(charing_st_id, None)

    def get_connected_charing_sts(self):
        try:
            charing_stations = (
                list(self.charing_stations.values())
                if len(self.charing_stations) > 0
                else []
            )
            return charing_stations
        except Exception as e:
            print("Error getting caller count:", e)
            return []

    ############################################## Callers Management #############################################

    async def save_charging_station(self, data: dict):

        charing_st_id = data["id"]
        if charing_st_id in self.charing_stations:
            await charing_collections.update_one({"id": charing_st_id}, {"$set": data})
            self.charing_stations[charing_st_id].update(data)
        else:
            await charing_collections.insert_one(data)
            self.charing_stations[charing_st_id] = data

        return self.charing_stations[charing_st_id]

    async def add_charing_st(self, charing_station: dict):

        try:

            resp = await charing_collections.insert_one(charing_station)
            inserted_id = str(resp.inserted_id)
            return (
                inserted_id
                and CharingStationInDB(
                    # **callers.serialize({**caller, "_id": inserted_id})
                    **charing_collections.serialize(
                        {**charing_station, "id": inserted_id}
                    )
                ).model_dump(by_alias=False)
                or None
            )
        except Exception as e:
            print("Error adding charing station:", e)
            return None

        # added_robot = await callers.find_by_id(inserted_id)
        # self.robots[inserted_id].update(robots.serialize(updated_robot))
        # self.callers[inserted_id] = callers.serialize(added_robot)
        # return self.callers[inserted_id]

    async def update_charing_st(self, charing_id: str, caller: dict):

        try:
            resp = await charing_collections.find_one_and_update(
                {"_id": charing_collections.to_object_id(charing_id)}, caller
            )
            return charing_collections.serialize(resp)
        except Exception as e:
            print("Error updating caller:", e)
            return None

        # if resp.modified_count > 0:
        #     updated_robot = await callers.find_by_id(caller_id)
        #     self.callers[caller_id].update(callers.serialize(updated_robot))
        #     return self.callers[caller_id]

    async def remove_charing_st(self, charing_id: str):
        resp = await charing_collections.delete_by_id(
            charing_collections.to_object_id(charing_id)
        )

        # if resp.deleted_count > 0:
        #     print("robot_id in self.robots", robot_id in self.callers)
        #     if robot_id in self.callers:
        #         del self.callers[robot_id]
        #     return {"status": "success", "message": "Robot deleted"}
        return True

    async def get_charing_st_list(self):
        try:
            resp = await charing_collections.find_list(page=1, page_size=10)
            return [
                CharingStationInDB(**charing_collections.serialize(doc)).model_dump(
                    by_alias=False
                )
                for doc in resp
            ]

        except Exception as e:
            print("Error getting caller count:", e)
            return []

    async def get_charing_st_by_id(self, charing_id: str):
        try:
            resp = await charing_collections.find_by_id(id=charing_id)
            resp = CharingStationInDB(**charing_collections.serialize(resp)).model_dump(
                by_alias=False
            )
            return resp or None

        except Exception as e:
            print("Error getting caller count:", e)
            return None
