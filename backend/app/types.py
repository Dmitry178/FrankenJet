""" Аннотированные типы """

from fastapi import Body
from typing import Annotated

status_ok = {"status": "ok"}

ABody = Annotated[str, Body()]
