from fastapi import APIRouter

from .views import (
    accounts,
)

router = APIRouter(prefix="/v1")
router.include_router(router=accounts.router)
