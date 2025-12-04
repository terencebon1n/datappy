from dataclasses import dataclass

from ..period import Period
from .description import Description
from .header import Header
from .informed_entity import InformedEntity


@dataclass(frozen=True)
class Alert:
    id: str
    active_period: Period
    informed_entity: InformedEntity
    header: Header
    description: Description
