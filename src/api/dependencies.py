from typing import Annotated

from fastapi import Depends

from .schemas import PaginationUseSchema

PaginationDep = Annotated[PaginationUseSchema, Depends()]
