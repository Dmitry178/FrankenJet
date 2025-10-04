""" Контекстный менеджер клиента S3 """

import aioboto3
import aiofiles
import json

from pathlib import Path
from typing import List, AsyncGenerator

from app.core.logs import logger


class S3Manager:
    """
    Менеджер S3
    """

    def __init__(
            self,
            access_key_id: str,
            secret_access_key: str,
            endpoint_url: str | None = None,
            # region_name: str = "us-east-1",
    ):
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.endpoint_url = endpoint_url
        # self.region_name = region_name
        self.session = aioboto3.Session()

    async def __aenter__(self):
        """
        Создание асинхронного клиента S3 при входе в контекст
        """

        self.client = await self.session.client(
            "s3",
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            endpoint_url=self.endpoint_url,
            # region_name=self.region_name,
        ).__aenter__()  # получаем фактический клиент

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Закрытие асинхронного клиента S3 при выходе из контекста
        """

        await self.client.__aexit__(exc_type, exc_val, exc_tb)  # закрываем клиент
        self.client = None

    async def get_client(self):
        """
        Создание асинхронного клиента S3
        """

        return self.session.client(
            "s3",
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            endpoint_url=self.endpoint_url,
            # region_name=self.region_name,
        )

    async def list_buckets(self) -> List[str]:
        """
        Возврат списка бакетов
        """

        async with await self.get_client() as s3:
            response = await s3.list_buckets()
            return [bucket["Name"] for bucket in response["Buckets"]]

    async def create_bucket(self, bucket: str, public=False) -> bool:
        """
        Создание бакета

        :param bucket: бакет
        :param public: флаг публичности бакета
        """

        try:
            async with await self.get_client() as s3:
                await s3.create_bucket(Bucket=bucket)
                logger.info(f"Бакет {bucket} создан")

            if public:
                await self.set_bucket_public_policy(bucket)

            return True

        except Exception as ex:
            logger.exception(f"Ошибка создания бакета {bucket}: {ex}")
            return False

    async def delete_bucket(self, bucket: str) -> bool:
        """
        Удаление бакета
        """

        try:
            async with await self.get_client() as s3:
                await self.empty_bucket(bucket)  # удаление всех объектов в бакете
                await s3.delete_bucket(Bucket=bucket)
                logger.info(f"Бакет {bucket} удалён")
                return True

        except Exception as ex:
            logger.exception(f"Ошибка удаления бакета {bucket}: {ex}")
            return False

    async def empty_bucket(self, bucket: str):
        """
        Очистка бакета от всех объектов
        """

        async with await self.get_client() as s3:
            objects = await s3.list_objects_v2(Bucket=bucket)  # получение списка объектов
            if "Contents" in objects:
                delete_keys = [{"Key": obj["Key"]} for obj in objects["Contents"]]
                await s3.delete_objects(
                    Bucket=bucket,
                    Delete={"Objects": delete_keys}
                )

    async def list_objects(self, bucket: str, prefix: str = "") -> List[dict]:
        """
        Возвращение списка объектов в бакете

        :param bucket: бакет
        :param prefix: фильтр путей внутри бакета
        """

        async with await self.get_client() as s3:
            response = await s3.list_objects_v2(
                Bucket=bucket,
                Prefix=prefix
            )
            return response.get("Contents", [])

    async def set_bucket_public_policy(self, bucket: str) -> bool:
        """
        Установка публичной политики для бакета (доступ на чтение)
        """

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{bucket}/*"]
                }
            ]
        }

        try:
            async with await self.get_client() as s3:
                await s3.put_bucket_policy(
                    Bucket=bucket,
                    Policy=json.dumps(policy)
                )
                logger.info(f"Политика публичного доступа установлена для бакета {bucket}")
                return True

        except Exception as ex:
            logger.exception(f"Ошибка установки политики для бакета {bucket}: {ex}")
            return False

    @staticmethod
    def define_content_type(file_name: str) -> dict:
        """
        Определение Content-Type по расширению файла
        """

        content_type_mapping = {
            # текстовые форматы
            ".txt": "text/plain",
            ".md": "text/markdown",
            ".csv": "text/csv",
            ".html": "text/html",
            ".htm": "text/html",
            ".css": "text/css",

            # изображения
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".svg": "image/svg+xml",
            ".svgz": "image/svg+xml",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".ico": "image/x-icon",
            ".bmp": "image/bmp",
            ".tiff": "image/tiff",
            ".tif": "image/tiff",

            # документы
            ".pdf": "application/pdf",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".xls": "application/vnd.ms-excel",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".ppt": "application/vnd.ms-powerpoint",
            ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",

            # архивы
            ".zip": "application/zip",
            ".rar": "application/x-rar-compressed",
            ".7z": "application/x-7z-compressed",
            ".tar": "application/x-tar",
            ".gz": "application/gzip",

            # json/xml
            ".json": "application/json",
            ".xml": "application/xml",
            ".rss": "application/rss+xml",

            # файлы кода
            ".js": "application/javascript",
            ".mjs": "application/javascript",

            # шрифты
            ".woff": "font/woff",
            ".woff2": "font/woff2",
            ".ttf": "font/ttf",
            ".otf": "font/otf",

            # аудио/видео
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav",
            ".mp4": "video/mp4",
            ".webm": "video/webm",
            ".ogg": "audio/ogg",
            ".avi": "video/x-msvideo",
        }

        extension = Path(file_name).suffix.lower()
        content_type = content_type_mapping.get(extension, "application/octet-stream")

        return {"ContentType": content_type}

    async def upload_file(
            self,
            bucket: str,
            local_file_path: str,
            s3_key: str | None = None,
            extra_args: dict | None = None
    ) -> bool:
        """
        Загрузка файла в S3

        :param bucket: бакет
        :param local_file_path: путь загружаемого файла на диске
        :param s3_key: путь к файлу внутри бакета
        :param extra_args: дополнительные аргументы
        """

        try:
            if s3_key is None:
                s3_key = Path(local_file_path).name

            async with await self.get_client() as s3:
                async with aiofiles.open(local_file_path, "rb") as file:
                    file_content = await file.read()

                upload_args = {"Bucket": bucket, "Key": s3_key, "Body": file_content}
                content_type = self.define_content_type(local_file_path)
                extra_args = extra_args | content_type if extra_args else content_type

                if extra_args:
                    upload_args.update(extra_args)

                await s3.put_object(**upload_args)
                logger.info(f"Файл {local_file_path} загружен в {s3_key}")
                return True

        except Exception as ex:
            logger.exception(f"Ошибка загрузки файла {local_file_path}: {ex}")
            return False

    async def download_file(self, bucket: str, local_file_path: str, s3_key: str) -> bool:
        """
        Скачивание файла из S3

        :param bucket: бакет
        :param local_file_path: путь загружаемого файла на диске
        :param s3_key: путь к файлу внутри бакета
        """

        try:
            async with await self.get_client() as s3:
                response = await s3.get_object(Bucket=bucket, Key=s3_key)
                async with aiofiles.open(local_file_path, "wb") as file:
                    async for chunk in response["Body"]:
                        await file.write(chunk)

                logger.info(f"Файл {s3_key} загружен в {local_file_path}")
                return True

        except Exception as ex:
            logger.exception(f"Ошибка загрузки файла {s3_key}: {ex}")
            return False

    async def delete_object(self, bucket: str, s3_key: str) -> bool:
        """
        Удаление объекта из S3

        :param bucket: бакет
        :param s3_key: путь к файлу внутри бакета
        """

        try:
            async with await self.get_client() as s3:
                await s3.delete_object(Bucket=bucket, Key=s3_key)
                logger.info(f"Объект {s3_key} удалён из {bucket}")
                return True

        except Exception as ex:
            logger.exception(f"Ошибка удаления объекта {s3_key}: {ex}")
            return False

    async def get_pre_signed_url(
            self,
            bucket: str,
            s3_key: str,
            expiration: int = 3600
    ) -> str | None:
        """
        Генерация предварительно подписанного URL
        """

        try:
            async with await self.get_client() as s3:
                url = await s3.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": bucket, "Key": s3_key},
                    ExpiresIn=expiration
                )
                return url

        except Exception as ex:
            logger.exception(f"Ошибка генерации предварительно подписанного  URL для {s3_key}: {ex}")
            return None

    async def copy_object(
            self,
            source_bucket: str,
            source_key: str,
            dest_bucket: str,
            dest_key: str
    ) -> bool:
        """
        Копирование объекта внутри S3
        """

        try:
            async with await self.get_client() as s3:
                copy_source = {"Bucket": source_bucket, "Key": source_key}
                await s3.copy_object(
                    CopySource=copy_source,
                    Bucket=dest_bucket,
                    Key=dest_key
                )
                logger.info(f"Объект скопирован из  {source_key} в {dest_key}")
                return True

        except Exception as ex:
            logger.exception(f"Ошибка копирования объекта {source_key}: {ex}")
            return False

    async def stream_download(
            self,
            bucket: str,
            s3_key: str
    ) -> AsyncGenerator[bytes, None]:
        """
        Потоковая загрузка файла
        """

        async with await self.get_client() as s3:
            response = await s3.get_object(Bucket=bucket, Key=s3_key)
            async for chunk in response["Body"]:
                yield chunk

    async def upload_from_memory(
            self,
            bucket: str,
            s3_key: str,
            data: bytes,
            content_type: str = "application/octet-stream"
    ) -> bool:
        """
        Загрузка данных из памяти
        """

        try:
            async with await self.get_client() as s3:
                await s3.put_object(
                    Bucket=bucket,
                    Key=s3_key,
                    Body=data,
                    ContentType=content_type
                )
                logger.info(f"Данные загружены в {s3_key}")
                return True

        except Exception as ex:
            logger.exception(f"Ошибка загрузки данных в {s3_key}: {ex}")
            return False

    async def get_object_metadata(
            self,
            bucket: str,
            s3_key: str
    ) -> dict | None:
        """
        Получает метаданные объекта
        """

        try:
            async with await self.get_client() as s3:
                response = await s3.head_object(Bucket=bucket, Key=s3_key)
                return response["Metadata"]

        except Exception as ex:
            logger.exception(f"Ошибка получения метаданных для {s3_key}: {ex}")
            return None
