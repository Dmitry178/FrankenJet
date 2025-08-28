from fastapi import APIRouter

from app.api.auth.routes.auth import auth_router
from app.api.auth.routes.oauth import oauth_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(oauth_router)
