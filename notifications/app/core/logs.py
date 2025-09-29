import logging
import sys

from app.core.config import bot_settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

bot_logger = logging.getLogger(bot_settings.APP_NAME)
