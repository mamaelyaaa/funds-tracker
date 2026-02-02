from fastapi import APIRouter

from .views import accounts, net_worth

router = APIRouter(prefix="/v1")
router.include_router(router=accounts.router)
router.include_router(router=net_worth.router)
