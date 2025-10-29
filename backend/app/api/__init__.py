from fastapi import APIRouter

from app.api.admin import admin_router
from app.api.aircraft import aircraft_router
from app.api.app import app_router
from app.api.articles import articles_router
from app.api.auth import auth_router
from app.api.bot import bot_router
from app.api.countries import countries_router
from app.api.facts import facts_router
from app.api.oauth2 import oauth_router
from app.api.pages import pages_router
from app.api.search import search_router
from app.api.tags import tags_router

router = APIRouter()

router.include_router(app_router)
router.include_router(admin_router)
router.include_router(auth_router)
router.include_router(oauth_router)
router.include_router(search_router)
router.include_router(pages_router)
router.include_router(articles_router)
router.include_router(facts_router)
router.include_router(tags_router)
router.include_router(aircraft_router)
router.include_router(countries_router)
router.include_router(bot_router)  # для тестирования бота
