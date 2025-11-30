from pydantic import BaseModel, Field


class SGigaChatAnswer(BaseModel):
    """
    Схема ответа GigaChat
    """

    answer: str = Field(..., description="Ответ LLM")
    prompt_tokens: int = Field(..., description="Количество токенов промта")
    completion_tokens: int = Field(..., description="Количество токенов ответа")
    total_tokens: int = Field(..., description="Всего токенов")
    precached_prompt_tokens: int = Field(..., description="Количество токенов кэша (истории)")
