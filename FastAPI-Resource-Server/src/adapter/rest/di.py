from fastapi import Depends, Query
from typing import Annotated

from ports.interfaces import dataManager
from config.container import container
from adapter.rest.dto import queryPagination


def get_pagination(
    offset: int | None = Query(None, ge=0),
    limit: int | None = Query(None, ge=1, le=100),
    order: str = Query("asc", pattern="^(asc|desc)$")
) -> queryPagination:
    return queryPagination(offset=offset, limit=limit, order=order)


PublicCrudDep = Annotated[dataManager, Depends(container.get_public_crud)]
PaginationDep = Annotated[queryPagination, Depends(get_pagination)]
