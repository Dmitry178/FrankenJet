from fastapi import APIRouter

from app.api.aircraft import aircraft_router
from app.api.app import app_router
from app.api.articles import articles_router
from app.api.auth import auth_router
from app.api.oauth2 import oauth_router

router = APIRouter()
router.include_router(app_router)
router.include_router(auth_router)
router.include_router(oauth_router)
router.include_router(aircraft_router)
router.include_router(articles_router)
