import csv
import logging

from abc import abstractmethod
from collections.abc import Iterable
from typing import Optional, Type, TypeVar, cast, get_args, get_origin

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, Session

from .gtfs_protocol import GTFSDataclassProtocol

TModel = TypeVar("TModel")
TDataclass = TypeVar("TDataclass", bound=GTFSDataclassProtocol)


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: \t %(message)s",
)

logger = logging.getLogger(__name__)


class GTFSModelBase[TDataclass](DeclarativeBase):
    item: TDataclass

    metadata = MetaData(schema="gtfs")

    @classmethod
    def _resolve_dataclass_type(cls) -> type[TDataclass]:
        dataclass_type: Optional[Type[TDataclass]] = None

        for base in cls.__orig_bases__:  # type: ignore[attr-defined]
            if get_origin(base) is GTFSModelBase:
                dataclass_type = get_args(base)[0]
                break

        if not dataclass_type:
            if hasattr(cls, "item") and isinstance(cls.item, TypeVar):
                raise TypeError(
                    f"Could not resolve TDataclass from base class of {cls.__name__}. "
                    "Ensure the model is defined like MyModel(GTFSModelBase[MyDataClass])."
                )

        return cast(Type[TDataclass], dataclass_type)

    def to_dataclass(self) -> TDataclass:
        dataclass_type = self.__class__._resolve_dataclass_type()
        return cast(TDataclass, dataclass_type.from_model(self))  # type: ignore[attr-defined]


class GTFSContainerBase[TDataclass, TModel]:
    items: list[TDataclass]

    def __init__(self) -> None:
        self.items = []

    @property
    def _resolve_dataclass(cls) -> TDataclass:
        return get_args(cls.__orig_bases__[0])[0]  # type: ignore[attr-defined]

    @property
    def _resolve_model(cls) -> TModel:
        return get_args(cls.__orig_bases__[0])[1]  # type: ignore[attr-defined]

    @property
    def _resolve_dataclass_type(cls) -> Type[TDataclass]:
        return cast(Type[TDataclass], cls._resolve_dataclass)

    @property
    def _resolve_model_type(cls) -> Type[TModel]:
        return cast(Type[TModel], cls._resolve_model)

    def to_models_iterable(self) -> Iterable[TModel]:
        return (item.to_model() for item in self.items)  # type: ignore[attr-defined]

    @abstractmethod
    def extract(self, file_data: csv.DictReader[str]) -> None: ...

    def load(self, session: Session, batch_size: int = 1000) -> None:
        if not self.items:
            return

        item_models = self.to_models_iterable()

        if not item_models:
            return

        batch: list[TModel] = []

        for i, item_model in enumerate(item_models):
            batch.append(item_model)
            if (i + 1) % batch_size == 0:
                try:
                    session.add_all(batch)
                    session.commit()
                except Exception as e:
                    session.rollback()
                    raise e
                batch = []

        if batch:
            try:
                session.add_all(batch)
                session.commit()
            except Exception as e:
                session.rollback()
                raise e

        logger.info(
            f"Initialized {len(self.items)} {self._resolve_dataclass_type.__name__}"
        )
