""" Создание бакетов S3 """

import asyncio
import logging
import sys

sys.path.append("/code")

from environs import Env

from app.config.app import BUCKET_IMAGES
from app.core.s3_manager import S3Manager


class S3Creator:
    """
    Инициализация S3
    """

    def __init__(self, s3manager: S3Manager):
        self.s3manager = s3manager
        assert s3manager, "Подключение к S3 отсутствует"

    async def create_buckets(self) -> None:
        """
        Создание бакетов
        """

        try:
            buckets_list = await self.s3manager.list_buckets()
            buckets_to_create = [BUCKET_IMAGES]

            for bucket in buckets_to_create:
                if bucket not in buckets_list:
                    await self.s3manager.create_bucket(bucket, public=True)
                    init_s3_logger.info(f"Бакет {bucket} создан")

        except Exception as ex:
            init_s3_logger.error(f"Ошибка инициализации S3: {ex}")


async def main() -> None:
    """
    Запуск скриптов инициализации S3
    """

    env = Env()
    env.read_env()

    access_key_id = env.str("S3_ACCESS_KEY_ID", None)
    secret_access_key = env.str("S3_SECRET_ACCESS_KEY", None)
    endpoint_url = env.str("S3_ENDPOINT_URL", None)

    if not access_key_id or not secret_access_key or not endpoint_url:
        return

    # создание экземпляра S3-менеджера
    s3_manager = S3Manager(
        access_key_id=access_key_id,
        secret_access_key=secret_access_key,
        endpoint_url=endpoint_url
    )

    init_s3_logger.info("Инициализация S3")
    await S3Creator(s3_manager).create_buckets()

    init_s3_logger.info("Инициализация S3 завершена")
    return None


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

init_s3_logger = logging.getLogger()

if __name__ == "__main__":
    asyncio.run(main())
