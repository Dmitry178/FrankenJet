from fastapi import Request

from app.schemas.api import SClientInfo


async def get_client_info(request: Request) -> SClientInfo:
    """
    Получение информации о клиенте
    """

    xff = None
    xff_all = request.headers.get("x-forwarded-for")
    if xff_all:
        # первый IP из списка (если их несколько)
        xff = xff_all.split(",")[0].strip()

    return SClientInfo(
        ip=request.client.host,
        xff=xff,
        xff_all=xff_all,
        user_agent=request.headers.get("user-agent"),
        real_ip=request.headers.get("x-real-ip"),
        referer=request.headers.get("referer"),
        accept_language=request.headers.get("accept-language"),
    )
