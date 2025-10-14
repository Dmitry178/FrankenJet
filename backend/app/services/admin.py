import json
import zipfile

from fastapi import UploadFile
from pathlib import Path
from tempfile import TemporaryDirectory

from app.core.db_manager import DBManager
from app.core.logs import logger


class AdminServices:

    db: DBManager | None

    def __init__(self, db: DBManager | None = None) -> None:
        self.db = db

    async def upload_file(self, file: UploadFile):
        """
        Загрузка и обработка zip-файла
        """

        """
        Пример mappings.json
        [
            {"model": "Article", "filename": "article.json", "type": "json", "resolve_content_from": ["content"]},
            {"model": "Aircraft", "filename": "aircraft.json", "type": "json", "resolve_content_from": None},
            {"model": "Facts", "filename": "facts.txt", "type": "text", "target_field": "fact"},
            {"model": "Tags", "filename": "tags.txt", "type": "text", "target_field": "tag_id"}
        ]
        """

        # mapping моделей
        models = {
            "Articles": self.db.articles,
            "Aircraft": self.db.aircraft.aircraft,
            "Tags": self.db.directory.tags,
        }

        with TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            zip_path = tmp_path / file.filename

            # загрузка и сохранение файла
            with zip_path.open("wb") as f:
                f.write(await file.read())

            # распаковка ZIP
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(tmp_path)

            # чтение mappings.json
            mappings_path = tmp_path / "mappings.json"
            if not mappings_path.exists():
                raise ValueError("mappings.json отсутствует в архиве")

            with mappings_path.open("r", encoding="utf-8") as f:
                mappings = json.load(f)

            # обработка каждого файла в соответствии с mappings.json
            for mapping in mappings:
                model_name = mapping["model"]  # название модели
                file_name = mapping["filename"]  # название загружаемого файла (json/text)
                file_path = tmp_path / file_name  # путь к файлу во временной директории
                file_type = mapping.get("type", "").lower()  # тип файла (json/text)
                resolve_content_from = mapping.get("resolve_content_from", [])  # список полей, куда подгружать файлы
                target_field = mapping.get("target_field")  # целевое поле загрузки данных

                model = models.get(model_name)
                if not model:
                    logger.warning(f'Модель "{model_name}" не найдена в списке допустимых моделей')
                    continue

                if not file_path.exists():
                    logger.warning(f'Файл "{file_name}" не найден для модели "{model_name}"')
                    continue

                with file_path.open("r", encoding="utf-8") as f:
                    if file_type == "json":
                        json_data = json.load(f)
                    elif file_type == "text":
                        text_data = f.read()
                    else:
                        logger.warning(f'Тип файла "{file_name}" не является "text" или "json"')
                        continue

                # обработка данных
                if file_type == "json":
                    # загрузка файлов, стыкуемых к json
                    for content_field in resolve_content_from:
                        content_file = json_data[content_field]
                        content_path = tmp_path / content_file
                        if not content_path.exists():
                            logger.warning(f'Файл "{content_file}" не найден для загрузки в "{file_name}"')
                            continue
                        with content_path.open("r", encoding="utf-8") as fc:
                            json_data[content_field] = fc.read()
                    result = json_data

                else:
                    # подготовка модели для загрузки текстового файла
                    result = [{target_field: line} for line in text_data]

                # загрузка данных в БД
                model.insert_all(result, commit=True)
