from fastapi import Depends, HTTPException, status, Header, Request
from src.helper.response import BadRequestError
from src.extension.db import user_action, users


async def verify_x_token(request: Request):
    try:

        x_token = request.headers.get("x_token")

        if not x_token:
            # return BadRequestError(msg="Invalid Request").send()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        resp = await user_action.find_one_by_conditions({"token_id": x_token})

        if not resp:
            # return BadRequestError(msg="Unauthorized").send()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        token = user_action.serialize(resp)
        user = users.find_one_by_conditions({"_id": token["user_id"]})

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
            detail="Invalid token",
        )


def verify_permission(action: str, resource: str):

    async def has_permission(current_user=Depends(verify_x_token)):
        print(action, resource)
        # role = current_user.get("role")
        # if not role:
        #     raise HTTPException(status_code=403, detail="Role not found")

        # permissions = role.get("permissions", {})
        # allowed = permissions.get(action, {}).get(resource, False)

        # if not allowed:
        #     raise HTTPException(
        #         status_code=403, detail=f"Permission denied: {action} {resource}"
        #     )
        return current_user

    return has_permission
