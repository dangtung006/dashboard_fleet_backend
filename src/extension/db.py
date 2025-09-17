from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from datetime import datetime
from bson import ObjectId


class DB_HELPER:
    def __init__(self):
        self.client = AsyncIOMotorClient("mongodb://localhost:27017/")
        self.db = self.client["esa_fleet_db"]
        self.page = 0
        self.page_size = 10

    def init_collection(self, collection):
        self.collection: AsyncIOMotorCollection = collection

    async def find_all(self):
        return self.collection.find({})

    async def find_all_by_conditions(self, conditions: dict):
        return self.collection.find(conditions)

    async def find_list(self, page, page_size, sort_key="", sort_dir=1):
        page = self.page if page == None else page
        page_size = self.page_size if page_size == None else page_size
        skip = (page - 1) * page_size
        return (
            self.collection.find({}).skip(skip).sort("created_at", -1).limit(page_size)
        )

    async def find_list_by_conditions(
        self, conditions, page, page_size, sort_key="", sort_dir=1
    ):
        skip = (page - 1) * page_size
        return (
            self.collection.find(conditions)
            .skip(skip)
            .limit(page_size)
            .sort(sort_key, sort_dir)
        )

    async def find_by_id(self, id):
        return await self.collection.find_one({"_id": ObjectId(id)})

    async def find_one_by_conditions(self, conditions: dict):
        return await self.collection.find_one(conditions)

    async def insert_one(self, data: dict):
        return await self.collection.insert_one(data)

    async def insert_many(self, data: dict):
        return await self.collection.insert_many(data)

    async def update_one(self, filter: dict, update: dict):
        # return await self.collection.update_one(filter=filter, update=update)
        return await self.collection.update_one(filter=filter, update={"$set": update})
        # self.collection.update_one({}, {"$set": {}}, upsert=True)

    async def update_by_id(self):
        return await self.collection.update_many(filter={}, update={})

    async def update_many(self, filter: dict, update: dict):
        return await self.collection.update_many(filter=filter, update=update)

    async def delete_one(self, filter):
        return await self.collection.delete_one(filter=filter)

    async def delete_by_id(self, id):
        obj_id = self.to_object_id(id)
        if not obj_id:
            return False
        return await self.collection.delete_one(filter={"_id": obj_id})

    async def delete_many(self, filter):
        return await self.collection.delete_many(filter=filter)

    async def count_all(self):
        return await self.collection.count_documents(filter={})

    async def count_by_conditions(self, conditions: dict):
        return await self.collection.count_documents(filter=conditions)

    async def create_idx(self, field):
        return await self.collection.create_index(field, expireAfterSeconds=0)

    # def handle_save(self, save_data: SAVE_DATA):
    #     id = save_data.id
    #     if not id:
    #         return self.insert_one(save_data.data)
    #     object_id = self.to_object_id(id)
    #     if object_id:
    #         return self.update_one({"_id": object_id}, update_data=save_data.data)

    def isValidObjectId(self, id: str):
        try:
            object_id = ObjectId(id)
            return object_id
        except:
            return False

    def to_object_id(self, id: str):
        return self.isValidObjectId(id) or False
        # if self.isValidObjectId(id):
        #     return self.isValidObjectId(id)
        # return False

    def serialize(self, doc: dict) -> dict:
        def convert_value(v):
            if isinstance(v, ObjectId):
                return str(v)
            elif isinstance(v, datetime):
                return v.isoformat()
            elif isinstance(v, dict):
                return self.serialize(v)
            elif isinstance(v, list):
                return [convert_value(i) for i in v]
            return v

        return {k: convert_value(v) for k, v in doc.items()}


class ROBOT_STATIONS(DB_HELPER):
    def __init__(self):
        super().__init__()
        self.init_collection(self.db["robot_stations"])


class ROBOTS(DB_HELPER):
    def __init__(self):
        super().__init__()
        self.init_collection(self.db["robots"])


class CALLERS(DB_HELPER):
    def __init__(self):
        super().__init__()
        self.init_collection(self.db["callers"])


class USERS(DB_HELPER):
    def __init__(self):
        super().__init__()
        self.init_collection(self.db["users"])

    async def get_users_with_roles(self):
        try:
            pipeline = [
                {
                    "$lookup": {
                        "from": "roles",  # collection role
                        "localField": "role_id",  # field trong user
                        "foreignField": "_id",  # field trong role
                        "as": "role",  # tên field output
                    }
                },
                {"$unwind": {"path": "$role", "preserveNullAndEmptyArrays": True}},
            ]
            return await self.collection.aggregate(pipeline).to_list(length=None)
        except Exception as E:
            print(str(E))
            return False

    async def get_user_detail_with_role(self, user_id):
        try:
            user = await self.collection.aggregate(
                [
                    {"$match": {"_id": ObjectId(user_id)}},
                    {
                        "$lookup": {
                            "from": "roles",  # collection role
                            "localField": "role_id",  # field trong users
                            "foreignField": "_id",  # field trong roles
                            "as": "role",  # output alias
                        }
                    },
                    {"$unwind": "$role"},  # lấy object thay vì mảng
                ]
            ).to_list(1)

            print("usererererererererrerererrerererrerererere:::", user[0])

            return user[0]

        except Exception as E:
            print(str(E))
            return False


class USER_ACTION(DB_HELPER):
    def __init__(self):
        super().__init__()
        self.init_collection(self.db["user_actions"])


class ROLES(DB_HELPER):
    def __init__(self):
        super().__init__()
        self.init_collection(self.db["roles"])


class ROBOT_MAPS(DB_HELPER):
    def __init__(self):
        super().__init__()
        self.init_collection(self.db["robot_maps"])


robot_stations = ROBOT_STATIONS()
robots = ROBOTS()
callers = CALLERS()
users = USERS()
roles = ROLES()
user_action = USER_ACTION()
robot_maps = ROBOT_MAPS()
