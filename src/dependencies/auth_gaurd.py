from fastapi import Depends, HTTPException, status, Header, Request
from src.helper.response import BadRequestError
from src.extension.db import user_action, users, roles


async def verify_x_token(request: Request):
    try:

        x_token = request.headers.get("x-token")
        print("x-token::", x_token)
        if not x_token:
            # return BadRequestError(msg="Invalid Request").send()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        resp = await user_action.find_one_by_conditions({"token_id": x_token})
        print("resp::", resp)

        if not resp:
            # return BadRequestError(msg="Unauthorized").send()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        token = user_action.serialize(resp)
        print("token::", token)
        user = await users.find_by_id(users.to_object_id(token["user_id"]))
        print("user::", user)

        if not user:
            # return BadRequestError(msg="Unauthorized").send()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        return {**user}
    except:
        # return BadRequestError(msg="Invalid Request").send()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )


def verify_permission(action: str, resource: str):

    async def has_permission(current_user=Depends(verify_x_token)):

        print(action, resource)

        role_id = current_user["role_id"]
        if not role_id:
            raise HTTPException(status_code=403, detail="Role not found")

        role = await roles.find_by_id(id=roles.to_object_id(role_id))
        permissions = role["permissions"]

        print("permissions:::", permissions)
        # permissions = role.get("permissions", {})
        allowed = permissions.get(action, {}).get(resource, False)

        print("allowed:::", allowed)

        if not allowed:
            raise HTTPException(
                status_code=403, detail=f"Permission denied: {action} {resource}"
            )
        return current_user

    return has_permission
