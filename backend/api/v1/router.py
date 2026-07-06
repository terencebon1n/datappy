from fastapi import APIRouter, Depends

from backend.api.v1.context import require_city

basic_router = APIRouter()

gtfs_router = APIRouter(dependencies=[Depends(require_city)])

gtfs_rt_router = APIRouter()

admin_router = APIRouter(prefix="/admin", tags=["admin"])
