from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from src.extension.db import users, roles
from src.helper.auth import SECRET_KEY, ALGORITHM
from src.helper.response import BadRequestError, NotFoundError, SuccessResponse
from bson import ObjectId

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
            # return BadRequestError(msg="Invalid token")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user = await users.find_one_by_conditions({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    role = await roles.find_one_by_conditions({"_id": ObjectId(user["role_id"])})
    user["role"] = role  # gắn luôn role object vào user
    return user


def require_permission(action: str, resource: str):
    async def permission_checker(current_user=Depends(get_current_user)):
        role = current_user.get("role")
        if not role:
            raise HTTPException(status_code=403, detail="Role not found")

        permissions = role.get("permissions", {})
        allowed = permissions.get(action, {}).get(resource, False)

        if not allowed:
            raise HTTPException(
                status_code=403, detail=f"Permission denied: {action} {resource}"
            )
        return current_user

    return permission_checker
