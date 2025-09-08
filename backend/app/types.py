""" Аннотированные типы """

from fastapi import Body
from typing import Annotated

status_ok = {"status": "ok"}
status_error = {"status": "error"}

ABody = Annotated[str, Body()]
