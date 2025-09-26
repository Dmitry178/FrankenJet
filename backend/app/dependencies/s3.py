from fastapi import Depends
from typing import Annotated

from app.core import settings, S3Manager


async def get_s3():
    """
    Dependency для FastAPI, предоставляющий S3Manager
    """

    access_key_id = settings.S3_ACCESS_KEY_ID
    secret_access_key = settings.S3_SECRET_ACCESS_KEY
    endpoint_url = settings.S3_ENDPOINT_URL

    async with S3Manager(
        access_key_id=access_key_id,
        secret_access_key=secret_access_key,
        endpoint_url=endpoint_url
    ) as s3_manager:
        yield s3_manager

DS3 = Annotated[S3Manager, Depends(get_s3)]
