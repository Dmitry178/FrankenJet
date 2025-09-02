from fastapi import APIRouter

from app.api.auth import auth_router
from app.api.oauth2 import oauth_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(oauth_router)
