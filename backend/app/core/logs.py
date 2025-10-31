""" Настройка логирования """

import logging
import sys

from app.config.env import settings


# конфиг логов
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(settings.APP_NAME)
