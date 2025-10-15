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

    async def find_list(
        self, page, page_size, sort_key="", sort_dir=1, exclude_fields=[]
    ):
        page = self.page if page == None else page
        page_size = self.page_size if page_size == None else page_size
        skip = (page - 1) * page_size
        return await (
            self.collection.find({}, {field: 0 for field in exclude_fields})
            .skip(skip)
            .sort("created_at", -1)
            .limit(page_size)
            .to_list(length=page_size)
        )

    async def find_list_by_conditions(
        self, conditions, page, page_size, sort_key="", sort_dir=1, exclude_fields=[]
    ):
        skip = (page - 1) * page_size
        return (
            self.collection.find(conditions, {field: 0 for field in exclude_fields})
            .skip(skip)
            .limit(page_size)
            .sort(sort_key, sort_dir)
            .to_list(length=page_size)
        )

    async def find_by_id(self, id):
        return await self.collection.find_one({"_id": ObjectId(id)})

    async def find_one_by_conditions(self, conditions: dict):
        return await self.collection.find_one(conditions)

    async def insert_one(self, data: dict):
        return await self.collection.insert_one(data)

    async def insert_many(self, data: dict):
        return await self.collection.insert_many(data)

    async def update_one(self, filter: dict, update: dict, upsert=False):
        # return await self.collection.update_one(filter=filter, update=update)
        return await self.collection.update_one(
            filter=filter, update={"$set": update}, upsert=upsert
        )

    async def update_one_v2(self, filter: dict, update: dict, upsert=False):
        return await self.collection.update_one(
            filter=filter, update=update, upsert=upsert
        )

    # self.collection.update_one({}, {"$set": {}}, upsert=True)

    async def update_by_id(self):
        return await self.collection.update_many(filter={}, update={})

    async def update_many(self, filter: dict, update: dict):
        return await self.collection.update_many(filter=filter, update=update)

    async def find_one_and_update(self, filter: dict, update: dict, upsert=False):
        return await self.collection.find_one_and_update(
            filter=filter, update={"$set": update}, upsert=upsert, return_document=True
        )

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

        return {f'{k == "_id" and "id" or k}': convert_value(v) for k, v in doc.items()}


class ROBOT_STATIONS(DB_HELPER):
    def __init__(self):
        super().__init__()
        self.init_collection(self.db["robot_stations"])


class ROBOTS(DB_HELPER):
    def __init__(self):
        super().__init__()
        self.init_collection(self.db["robots"])

    async def get_robot_with_map(self, robot_id):
        try:
            robot = await self.collection.aggregate(
                [
                    {"$match": {"_id": ObjectId(robot_id)}},
                    {
                        "$lookup": {
                            "from": "robot_maps",  # collection robot_maps
                            "localField": "robot_map",  # field trong robots
                            "foreignField": "_id",  # field trong robot_maps
                            "as": "current_map",  # output alias
                        }
                    },
                    {"$unwind": "$current_map"},  # lấy object thay vì mảng
                ]
            ).to_list(1)

            return robot[0]

        except Exception as E:
            print(str(E))
            return False


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
                # {"$unwind": {"path": "$role", "preserveNullAndEmptyArrays": True}},
                {
                    "$unwind": {
                        "path": "$role",
                        "preserveNullAndEmptyArrays": True,  # giữ lại user nếu không có role
                    }
                },  # lấy object thay vì mảng
                {
                    "$addFields": {
                        "role": {"$ifNull": ["$role", {}]}  # nếu null thì set {}
                    }
                },
            ]
            return await self.collection.aggregate(pipeline).to_list(length=None)
        except Exception as E:
            print(str(E))
            return False

    async def get_filter_user(
        self, page: int = 1, page_size: int = 10, search: str = "", role: str = ""
    ):
        try:
            skip = (page - 1) * page_size
            pipeline = []

            # 1. Search theo name/email/phone
            if search:
                pipeline.append(
                    {
                        "$match": {
                            "$or": [
                                {"name": {"$regex": search, "$options": "i"}},
                                # {"email": {"$regex": search, "$options": "i"}},
                                # {"phone": {"$regex": search, "$options": "i"}},
                            ]
                        }
                    }
                )

            # 2. Join với roles
            pipeline += [
                {
                    "$lookup": {
                        "from": "roles",
                        "localField": "role_id",
                        "foreignField": "_id",
                        "as": "role",
                    }
                },
                {"$unwind": {"path": "$role", "preserveNullAndEmptyArrays": True}},
                {"$addFields": {"role": {"$ifNull": ["$role", {}]}}},
            ]

            # 3. Lọc role (nếu khác All)
            if role and role.lower() != "all":
                pipeline.append(
                    {"$match": {"role.name": {"$regex": f"^{role}$", "$options": "i"}}}
                )

            # 4. Dùng facet cho phân trang + totalCount
            pipeline.append(
                {
                    "$facet": {
                        "users": [
                            # {"$sort": {"created_at": -1}},
                            {"$skip": skip},
                            {"$limit": page_size},
                        ],
                        # "pagination": [
                        #     {"$count": "count"},
                        # ],
                        "total_count": [{"$count": "count"}],
                        # "page": page,
                        # "page_size": page_size,
                    }
                }
            )
            resp = await self.collection.aggregate(pipeline).to_list(length=1)
            return self.serialize(len(resp) > 0 and resp[0] or {})

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
                    {
                        "$unwind": {
                            "path": "$role",
                            "preserveNullAndEmptyArrays": True,  # giữ lại user nếu không có role
                        }
                    },  # lấy object thay vì mảng
                    {
                        "$addFields": {
                            "role": {"$ifNull": ["$role", {}]}  # nếu null thì set {}
                        }
                    },
                ]
            ).to_list(1)

            return user and len(user) > 0 and user[0] or None
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

    async def get_roles_with_members(self, page: int = 1, page_size: int = 10):
        skip = (page - 1) * page_size

        try:
            pipeline = [
                {
                    "$lookup": {
                        "from": "users",
                        "let": {"roleId": "$_id"},
                        "pipeline": [
                            {"$match": {"$expr": {"$eq": ["$role_id", "$$roleId"]}}},
                            {"$count": "count"},
                        ],
                        "as": "userCounts",
                    }
                },
                {
                    "$addFields": {
                        "members_count": {
                            "$ifNull": [{"$arrayElemAt": ["$userCounts.count", 0]}, 0]
                        }
                    }
                },
                {"$project": {"userCounts": 0}},  # bỏ field tạm
                # {"$sort": {"name": 1}},
                {"$skip": skip},
                {"$limit": page_size},
            ]

            roles = await self.collection.aggregate(pipeline).to_list(length=None)
            return roles

        except Exception as E:
            print(str(E))
            return False


class ROBOT_MAPS(DB_HELPER):
    def __init__(self):
        super().__init__()
        self.init_collection(self.db["robot_maps"])


class CHARING_STATIONS(DB_HELPER):
    def __init__(self):
        super().__init__()
        self.init_collection(self.db["charing_stations"])


class ROBOT_STATISTICS(DB_HELPER):
    def __init__(self):
        super().__init__()
        self.init_collection(self.db["robot_statistics"])

    async def get_stats_with_robot(self):
        try:
            pipeline = [
                {
                    "$lookup": {
                        "from": "robots",  # collection robots
                        "localField": "robot_id",  # field trong robot statistics
                        "foreignField": "_id",  # field trong role
                        "as": "robot",  # tên field output
                    }
                },
                {"$unwind": {"path": "$robot", "preserveNullAndEmptyArrays": True}},
            ]
            return await self.collection.aggregate(pipeline).to_list(length=None)

        except Exception as E:
            print(str(E))
            return False


robot_stations = ROBOT_STATIONS()
robot_statistics = ROBOT_STATISTICS()
robots = ROBOTS()
callers = CALLERS()
charing_stations = CHARING_STATIONS()
users = USERS()
roles = ROLES()
user_action = USER_ACTION()
robot_maps = ROBOT_MAPS()
