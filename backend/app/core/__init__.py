from app.core.config_env import settings
from app.core.s3_manager import S3Manager

s3_manager = S3Manager(
    access_key_id=settings.S3_ACCESS_KEY_ID,
    secret_access_key=settings.S3_SECRET_ACCESS_KEY,
    endpoint_url=settings.S3_ENDPOINT_URL,
)
