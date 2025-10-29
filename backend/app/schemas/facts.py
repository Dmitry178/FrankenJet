from pydantic import BaseModel, Field


class SFacts(BaseModel):
    """
    Схема фактов об авиации
    """

    fact: str = Field(..., max_length=256, description="Факт об авиации")
