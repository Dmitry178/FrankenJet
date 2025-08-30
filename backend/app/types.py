""" Аннотированные типы """

from fastapi import Body
from typing import Annotated

status_ok = {"status": "OK"}

ABody = Annotated[str, Body()]
