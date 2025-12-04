from collections.abc import Iterable
from typing import Optional, Type, TypeVar, cast

from sqlalchemy import MetaData, create_engine, delete
from sqlalchemy.orm import DeclarativeBase, Session

from ..config import postgres_url
from .gtfs_protocol import GTFSDataclassProtocol

TModel = TypeVar("TModel")
TDataclass = TypeVar("TDataclass", bound=GTFSDataclassProtocol)


class GTFSModelBase[TDataclass](DeclarativeBase):
    item: TDataclass

    metadata = MetaData(schema="gtfs")
    engine = create_engine(postgres_url, client_encoding="utf8")

    @classmethod
    def _resolve_dataclass_type(cls) -> type[TDataclass]:
        from typing import get_args, get_origin

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
        GTFSModelBase.metadata.create_all(GTFSModelBase.engine)

    def to_models_iterable(self) -> Iterable[TModel]:
        return (item.to_model() for item in self.items)  # type: ignore[attr-defined]

    def delete(self, session: Session) -> None:
        try:
            if not self.items:
                return

            item_dataclass: TDataclass = self.items[0]
            item_model: TModel = item_dataclass.to_model()  # type: ignore[attr-defined]

            delete_stmt = delete(item_model.__table__)  # type: ignore[attr-defined]
            session.execute(delete_stmt)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error during initial table deletion: {e}")
            raise e

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
