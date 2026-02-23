from __future__ import annotations

from enum import StrEnum
from typing import Union

import pyspark.sql.functions as sf
from pyspark.sql.column import Column


class SparkPath:
    def __init__(self, path: str) -> None:
        self.path = path

    def __truediv__(self, other: Union[str, StrEnum, SparkPath]) -> SparkPath:
        return SparkPath(f"{self.path}.{str(other)}")

    def __str__(self) -> str:
        return self.path

    @property
    def col(self) -> Column:
        return sf.col(str(self))

    def alias(self, name: str) -> Column:
        return self.col.alias(name)


class SparkColumns(StrEnum):
    def __truediv__(self, other: Union[str, SparkColumns]) -> SparkPath:
        return SparkPath(f"{self.value}.{str(other)}")

    def __str__(self) -> str:
        return self.value

    @property
    def col(self) -> Column:
        return sf.col(str(self))
