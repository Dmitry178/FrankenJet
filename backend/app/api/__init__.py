from fastapi import APIRouter

from app.api.aircraft import aircraft_router
from app.api.app import app_router
from app.api.articles import articles_router
from app.api.auth import auth_router
from app.api.bureaus import bureaus_router
from app.api.countries import countries_router
from app.api.designers import designers_router
from app.api.manufacturers import manufacturers_router
from app.api.oauth2 import oauth_router
from app.api.pages import pages_router

router = APIRouter()
router.include_router(app_router)
router.include_router(auth_router)
router.include_router(oauth_router)
router.include_router(pages_router)
router.include_router(articles_router)
router.include_router(aircraft_router)
router.include_router(countries_router)
router.include_router(bureaus_router)
router.include_router(designers_router)
router.include_router(manufacturers_router)
