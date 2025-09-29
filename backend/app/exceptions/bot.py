from fastapi import HTTPException
from starlette import status

bot_user_forbidden_403 = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
