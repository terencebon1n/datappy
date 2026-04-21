from fastapi import APIRouter, Depends

from src.api.v1.context import set_city_context

gtfs_router = APIRouter(dependencies=[Depends(set_city_context)])

gtfs_rt_router = APIRouter()
