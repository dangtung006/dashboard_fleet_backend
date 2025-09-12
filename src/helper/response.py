from fastapi.responses import JSONResponse
from fastapi import status


class BaseResponse:
    def __init__(self, msg, status):
        self.msg = msg
        self.status = status

    def send(self, data, header={}):
        return JSONResponse(
            status_code=self.status,
            content={"code": self.status, "msg": self.msg, "data": data},
            headers=header,
        )


class BaseErrResponse:
    def __init__(self, msg, status):
        self.msg = msg
        self.status = status

    def send(self):
        return JSONResponse(
            status_code=self.status, content={"code": self.status, "msg": self.msg}
        )


class SuccessResponse(BaseResponse):
    def __init__(self, msg):

        super().__init__(msg=msg, status=status.HTTP_200_OK)


class CreatedResponse(BaseResponse):
    def __init__(self, msg):
        super().__init__(msg=msg, status=status.HTTP_201_CREATED)


class BadRequestError(BaseErrResponse):
    def __init__(self, msg):
        super().__init__(msg=msg, status=status.HTTP_400_BAD_REQUEST)


class UnauthorizedError(BaseErrResponse):
    def __init__(self, msg):
        super().__init__(msg=msg, status=status.HTTP_401_UNAUTHORIZED)


class ForbiddenError(BaseErrResponse):
    def __init__(self, msg):
        super().__init__(msg=msg, status=status.HTTP_403_FORBIDDEN)


class NotFoundError(BaseErrResponse):
    def __init__(self, msg):
        super().__init__(msg=msg, status=status.HTTP_404_NOT_FOUND)


class InternalServerError(BaseErrResponse):
    def __init__(self, msg):
        super().__init__(msg=msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
