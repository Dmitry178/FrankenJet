from pydantic import BaseModel


class SLogEntry(BaseModel):
    """
    Схема логов
    """

    level: str
    message: str
    module: str
    funcName: str
    lineno: int
    asctime: str
    exc_text: str | None = None
    stack_info: str | None = None
    traceback: str | None = None
