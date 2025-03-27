"""Models for Bwee Tech API."""

from dataclasses import dataclass
from typing import Generic, TypeVar

from .utils import json_to_bean

T = TypeVar("T")


@dataclass
class ResultData(Generic[T]):
    """Result data."""

    arr: list[T] = None
    obj: T = None
    len: int = 0


@dataclass
class Result(Generic[T]):
    """Result."""

    code: int = None
    msg: str = None
    data: ResultData[T] = None

    def is_ok(self) -> bool:
        """Return True if the result is OK."""
        return self.code == 0


# 修改parse_result函数以支持类型参数
def parse_result(json_data: str, data_type: type[T]) -> Result[T]:
    """转换JSON到Result对象，需指定具体数据类型."""
    result = json_to_bean(json_data, Result[data_type])
    if result.data and result.data.arr:
        result.data.len = len(result.data.arr)
    return result
