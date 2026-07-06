from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase


class GTFSModelBase(DeclarativeBase):
    metadata = MetaData(schema="gtfs")
