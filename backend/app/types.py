""" Аннотированные типы """

from enum import Enum
from fastapi import Body
from typing import Annotated


class StatusEnum(str, Enum):
    ok = "ok"
    error = "error"


status_ok = {"status": StatusEnum.ok}
status_error = {"status": StatusEnum.error}

ABody = Annotated[str, Body()]
