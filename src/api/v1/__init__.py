from fastapi import APIRouter

from .views import accounts, histories, goals, net_worth

router = APIRouter(prefix="/v1")

router.include_router(router=accounts.router)
router.include_router(router=histories.router)
router.include_router(router=goals.router)
router.include_router(router=net_worth.router)
