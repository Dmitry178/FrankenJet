import logging
import sys

from app.config import app_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

app_logger = logging.getLogger(app_settings.APP_NAME)
