from functools import wraps

from sqlalchemy.exc import IntegrityError, SQLAlchemyError, MultipleResultsFound, NoResultFound

from app.core.logs import logger
from app.exceptions.base import DatabaseServiceError, ServiceError, DatabaseUniqueFieldError, BaseCustomException, \
    DatabaseMultipleResultsError, DatabaseNoResultError


def handle_basic_db_errors(func):
    """
    Декоратор для обработки основных ошибок базы данных
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)

        except BaseCustomException as ex:
            raise ex

        except NoResultFound as ex:
            logger.warning(ex)
            raise DatabaseNoResultError from ex

        except MultipleResultsFound as ex:
            logger.warning(ex)
            raise DatabaseMultipleResultsError from ex

        except IntegrityError as ex:
            if getattr(ex.orig, 'pgcode', None) == "23505":
                logger.warning(ex)
                raise DatabaseUniqueFieldError from ex
            else:
                logger.error(ex)
                raise DatabaseServiceError from ex

        except SQLAlchemyError as ex:
            logger.error(ex)
            raise DatabaseServiceError from ex

        except AttributeError as ex:
            # ошибка кода
            logger.exception(ex)
            raise ServiceError from ex

        except Exception as ex:
            # прочие ошибки
            logger.exception(ex)
            raise ServiceError from ex

    return wrapper
