from uuid import UUID

from fastapi import Request
from user_agents import parse

from app.core.db_manager import DBManager
from app.core.logs import logger
from app.schemas.user_info import SClientInfo, SUserAgentInfo


class UserInfoServices:

    db: DBManager | None

    def __init__(self, db: DBManager | None = None) -> None:
        self.db = db

    @staticmethod
    def get_client_info(request: Request) -> SClientInfo:
        """
        Получение информации о клиенте
        """

        xff = None
        xff_all = request.headers.get("x-forwarded-for")
        if xff_all:
            # первый IP из списка (если их несколько)
            xff = xff_all.split(",")[0].strip()

        accept_language = request.headers.get("accept-language")
        user_agent = request.headers.get("user-agent")
        user_agent_parce = parse(user_agent or "")

        user_agent_info = SUserAgentInfo(
            is_ru="ru" in (accept_language or "").lower(),
            is_bot=user_agent_parce.is_bot or accept_language is None or user_agent is None,
            is_tablet=user_agent_parce.is_tablet,
            is_mobile=user_agent_parce.is_mobile,
            is_touch_capable=user_agent_parce.is_touch_capable,
            is_pc=user_agent_parce.is_pc,
            os_family=user_agent_parce.os.family,
            os_version=user_agent_parce.os.version_string,
            device_family=user_agent_parce.device.family,
            device_brand=user_agent_parce.device.brand,
            device_model=user_agent_parce.device.model,
            browser_family=user_agent_parce.browser.family,
            browser_version=user_agent_parce.browser.version_string,
        )

        return SClientInfo(
            ip=request.client.host,
            xff=xff,
            xff_all=xff_all,
            user_agent=user_agent,
            user_agent_parce=str(user_agent_parce),
            real_ip=request.headers.get("x-real-ip"),
            referer=request.headers.get("referer"),
            accept_language=accept_language,
            user_agent_info=user_agent_info,
        )

    def notification_message(self, user_id: UUID, user: str, request: Request) -> dict:
        """
        Подготовка текста уведомления
        """

        try:
            client_info = self.get_client_info(request)
            ip = client_info.ip
            user_agent = client_info.user_agent_parce

        except Exception as ex:
            logger.exception("Ошибка парсинга User-Agent", extra={"error": str(ex)})
            ip = None
            user_agent = None

        message = {
            "id": str(user_id),
            "user": user,
            "client-ip": ip,
            "user-agent": user_agent,
        }

        return message
