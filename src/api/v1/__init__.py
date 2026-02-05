from fastapi import APIRouter

from .views import accounts, histories

router = APIRouter(prefix="/v1")

router.include_router(router=accounts.router)
router.include_router(router=histories.router)
