from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from .gtfs_base import GTFSModelBase


class GTFSDataclassProtocol(Protocol):
    @classmethod
    def from_model(
        cls, model: GTFSModelBase[GTFSDataclassProtocol]
    ) -> GTFSDataclassProtocol: ...
