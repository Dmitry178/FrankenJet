from functools import wraps

import asyncpg
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, MultipleResultsFound, NoResultFound

from app.exceptions.base import DatabaseServiceError, ServiceError, DatabaseUniqueFieldError, BaseCustomException, \
    DatabaseMultipleResultsError, DatabaseNoResultError


def handle_basic_db_errors(func):
    """
    Декоратор для обработки ошибок IntegrityError и SQLAlchemyError
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)

        except BaseCustomException as ex:
            raise ex

        except NoResultFound as ex:
            raise DatabaseNoResultError from ex

        except MultipleResultsFound as ex:
            raise DatabaseMultipleResultsError from ex

        except IntegrityError as ex:
            orig = ex.orig
            if isinstance(orig, asyncpg.exceptions.UniqueViolationError):
                raise DatabaseUniqueFieldError from ex
            else:
                raise DatabaseServiceError from ex

        except SQLAlchemyError as ex:
            raise DatabaseServiceError from ex

        except Exception as ex:
            raise ServiceError from ex

    return wrapper
