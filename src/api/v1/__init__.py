from fastapi import APIRouter

from .views import accounts, histories, goals

router = APIRouter(prefix="/v1")

router.include_router(router=accounts.router)
router.include_router(router=histories.router)
router.include_router(router=goals.router)
