from fastapi import APIRouter, Response, Request, Header, Depends

# from fastapi.security import OAuth2PasswordRequestForm
# from passlib.hash import bcrypt
from uuid import uuid4
import datetime

# from src.helper.auth import create_access_token
from src.helper.response import (
    BadRequestError,
    NotFoundError,
    SuccessResponse,
    InternalServerError,
)

from src.extension.db import users, roles, user_action
from src.dto.user import UserCreate, UserInDB
from src.dto.auth import AuthBase
from src.dependencies.auth_gaurd import verify_x_token

# from bson import ObjectId

auth_route = APIRouter(tags=["Auth"])


# @auth_route.post("/login/oauth2", response_model=UserInDB)
# async def login_oauth2(form_data: OAuth2PasswordRequestForm = None):

#     try:
#         user = await users.find_one_by_conditions({"email": form_data.username})

#         if not user:
#             return BadRequestError("Invalid User")

#         if not bcrypt.verify(form_data.password, user["password_hash"]):
#             return BadRequestError("Invalid email or password")

#         token = create_access_token(
#             {
#                 "sub": str(user["_id"]),
#                 "email": user["email"],
#                 "role_id": str(user["role_id"]),
#             }
#         )

#         return {"access_token": token, "token_type": "bearer"}

#     except Exception as E:
#         return InternalServerError(msg=str(E))


@auth_route.post("/login")
async def login(request: Request, response: Response, formData: AuthBase):

    try:
        req_body = formData.dict()
        user = await users.find_one_by_conditions({"email": req_body["email"]})

        if not user:
            return BadRequestError("Invalid User").send()
        user = users.serialize(user)

        print("user:::", user)
        print("user:::", user["_id"])

        session_id = str(uuid4())
        print("session_id:::", session_id)
        now = datetime.datetime.utcnow()
        expire_at = now + datetime.timedelta(minutes=2)

        token = await user_action.insert_one(
            {
                "token_id": session_id,
                "user_id": user["_id"],
                "created_at": now,
                "expireAt": expire_at,
            }
        )

        print("token:::", token)

        if not token:
            return BadRequestError("Invalid Token").send()
        # response.set_cookie(key=session_id, value="tundang", httponly=True, max_age=100)
        # token = user_action.serialize(token)
        return SuccessResponse(msg="OK").send(data={**user, "token": session_id})

    except Exception as E:
        print(E)
        return InternalServerError(msg=str(E)).send()


@auth_route.post("/logout")
async def logout(request: Request, response: Response, formData: AuthBase):

    try:
        # req_body = formData.dict()
        # user = await users.find_one_by_conditions({"email": req_body["email"]})

        # if not user:
        #     return BadRequestError("Invalid User")
        # user = users.serialize(user)

        # print("user:::", user)
        # print("user:::", user["_id"])

        # session_id = str(uuid4())
        # print("session_id:::", session_id)

        # response.set_cookie(key=session_id, value="tundang", httponly=True, max_age=100)

        # return SuccessResponse(msg="OK").send(data={**user, "token": session_id})
        pass

    except Exception as E:
        print(E)
        return InternalServerError(msg=str(E)).send()


@auth_route.get("/me")
async def check_user(
    request: Request, response: Response, x_token: str = Depends(verify_x_token)
):
    try:
        # session_val = request.cookies.get(session)
        # print("session_val::", session_val)
        # if not session_val:
        #     return BadRequestError(msg="Invalid Token")
        # all_headers = request.headers
        # user_agent = request.headers.get("user-agent")
        # custom_header = request.headers.get("x-custom-header")
        # resp = await user_action.find_one_by_conditions({"token_id": session})
        # print(resp)
        # return SuccessResponse(msg="OK").send(data=user_action.serialize(resp))
        return SuccessResponse(msg="OK").send(data=x_token)
        # return x_token

    except Exception as E:
        return InternalServerError(msg=str(E))
