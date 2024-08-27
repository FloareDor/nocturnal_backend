import logging
import random
import string
from functools import wraps

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncConnection

logger = logging.getLogger(__name__)

ALPHA_NUM = string.ascii_letters + string.digits


def generate_random_alphanum(length: int = 20) -> str:
    return "".join(random.choices(ALPHA_NUM, k=length))


def transactional():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Find the db_connection in the arguments
            db_connection = next(
                (arg for arg in args if isinstance(arg, AsyncConnection)),
                kwargs.get("db_connection"),
            )

            if not db_connection:
                raise ValueError("Database connection not provided")

            try:
                async with db_connection.begin():
                    return await func(*args, **kwargs)
            except Exception as e:
                # The transaction will automatically be rolled back
                if isinstance(e, HTTPException):
                    raise e
                elif isinstance(e, SQLAlchemyError):
                    raise HTTPException(
                        status_code=500, detail=f"Database error: {str(e)}"
                    )
                else:
                    raise HTTPException(
                        status_code=500, detail=f"Unexpected error: {str(e)}"
                    )

        return wrapper

    return decorator
