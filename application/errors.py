from http import HTTPStatus


# =======================# .=========FILE WHERE CAN CREATE YOURSELF ERRORS IN PROJECT ====================================
class BaseProjectException(Exception):
    message: str = 'Oops'
    code: int = 500

    def __init__(self, message: str = '', *, code: int = 500):
        super().__init__()
        if message:
            self.message = message
        self.code = code


class ConflictError(BaseProjectException):
    def __init__(self, message: str = 'Record already exists'):
        super().__init__(message, code=HTTPStatus.CONFLICT)


class AuthenticationErrors(BaseProjectException):
    def __init__(self, message: str = 'Invalid credentials'):
        super().__init__(message, code=HTTPStatus.UNAUTHORIZED)


class BadRequestErrors(BaseProjectException):
    def __init__(self, message: str = 'Bad request'):
        super().__init__(message, code=HTTPStatus.BAD_REQUEST)


class RequestFromAuthorizedAccountErrors(BaseProjectException):
    def __init__(self, message: str = 'Request from an authorized account'):
        super().__init__(message, code=HTTPStatus.FORBIDDEN)


class NotFoundErrors(BaseProjectException):
    def __init__(self, message: str = 'Not Found'):
        super().__init__(message, code=HTTPStatus.NOT_FOUND)
