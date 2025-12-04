from dataclasses import dataclass

from ...text import Text


@dataclass(frozen=True)
class Header:
    text: Text
