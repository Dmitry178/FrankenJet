""" Аннотированные типы """

from fastapi import Body

from typing import Annotated

ABody = Annotated[str, Body()]
