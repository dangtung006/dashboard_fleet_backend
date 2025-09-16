from .base import BaseDTO
from pydantic import BaseModel, Field
from typing import Optional


class PermissionGroup(BaseModel):
    user: bool = False
    robot: bool = False
    role_and_permission: bool = False
    charging_station: bool = False
    dashboard: bool = False
    user_information: bool = False
    robot_information: bool = False
    statics: bool = False


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
    permissions: Permissions = Permissions()


class RoleCreate(RoleBase):
    pass


class RoleInDB(RoleBase):
    id: str
