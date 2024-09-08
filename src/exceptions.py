from typing import Any, Dict, List, Optional

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.schemas import CustomModel


class ErrorDetail(CustomModel):
    loc: List[str] = ["body"]
    msg: str
    type: str


class ErrorResponse(CustomModel):
    detail: str  # Main field for error messages
    details: Optional[List[ErrorDetail]] = None  # Optional field for detailed errors
    type: Optional[str] = None  # Field to store the exception type


class DetailedHTTPException(HTTPException):
    STATUS_CODE = status.HTTP_500_INTERNAL_SERVER_ERROR
    DETAIL = "Server error"

    def __init__(
        self, status_code: int = None, detail: str = None, **kwargs: Dict[str, Any]
    ) -> None:
        self.status_code = status_code or self.STATUS_CODE
        self.detail = detail or self.DETAIL
        super().__init__(status_code=self.status_code, detail=self.detail, **kwargs)


class PermissionDenied(DetailedHTTPException):
    STATUS_CODE = status.HTTP_403_FORBIDDEN
    DETAIL = "Permission denied"


class NotFound(DetailedHTTPException):
    STATUS_CODE = status.HTTP_404_NOT_FOUND
    DETAIL = "Not found"


class BadRequest(DetailedHTTPException):
    STATUS_CODE = status.HTTP_400_BAD_REQUEST
    DETAIL = "Bad Request"


class NotAuthenticated(DetailedHTTPException):
    STATUS_CODE = status.HTTP_401_UNAUTHORIZED
    DETAIL = "User not authenticated"

    def __init__(self) -> None:
        super().__init__(headers={"WWW-Authenticate": "Bearer"})


class DetailedError(DetailedHTTPException):
    def __init__(
        self, exception: Exception, status_code: int = status.HTTP_400_BAD_REQUEST
    ) -> None:
        super().__init__(status_code=status_code, detail=str(exception))
        self.original_exception = exception

    def to_dict(self) -> Dict[str, Any]:
        return {
            "detail": str(self.detail),
            "type": type(self.original_exception).__name__,
        }


def clean_error_message(message: str) -> str:
    """Remove the generic 'Value error, ' prefix from error messages."""
    if message.startswith("Value error, "):
        return message.split(", ", 1)[1]
    return message


async def unified_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, RequestValidationError):
        errors = [
            ErrorDetail(loc=error["loc"], msg=error["msg"], type=error["type"])
            for error in exc.errors()
        ]
        message = "; ".join([error.msg for error in errors])
        message = clean_error_message(message)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(
                detail=message, details=errors, type="RequestValidationError"
            ).dict(),
        )
    elif isinstance(exc, DetailedError):
        return JSONResponse(
            status_code=exc.status_code, content=ErrorResponse(**exc.to_dict()).dict()
        )
    elif isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                detail=str(exc.detail), type=exc.__class__.__name__
            ).dict(),
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                detail="An unexpected error occurred", type=type(exc).__name__
            ).dict(),
        )
