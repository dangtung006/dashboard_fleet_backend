from .base import BaseDTO
from pydantic import BaseModel, Field
from typing import Optional, Optional


class PermissionGroup(BaseModel):
    monitor: bool = False
    robot: bool = False
    robot_detail: bool = False
    caller: bool = False
    charging_station: bool = False
    user: bool = False
    user_detail: bool = False
    statistics: bool = False


class Permissions(BaseModel):
    add: PermissionGroup = PermissionGroup()
    view: PermissionGroup = PermissionGroup()
    edit: PermissionGroup = PermissionGroup()
    delete: PermissionGroup = PermissionGroup()


class PermisionUpdate(BaseModel):
    resource: str
    action: str
    val: bool


class RoleBase(BaseModel):
    name: str = Field(..., example="Leader")
    status: Optional[int] = 1
    permissions: Permissions = Permissions()


class RoleCreate(RoleBase):
    pass


class RoleInDB(RoleBase):
    id: str
