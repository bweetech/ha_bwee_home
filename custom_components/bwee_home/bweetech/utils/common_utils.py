"""Common utility functions for Bwee Home integration."""

from dataclasses import asdict, fields, is_dataclass
import json
from typing import Any, TypeVar, get_args, get_origin, get_type_hints

T = TypeVar("T")


def _replace_typevars(tp: Any, type_var_map: dict[TypeVar, type]) -> Any:
    """递归替换类型中的TypeVar为实际类型."""
    if isinstance(tp, TypeVar):
        return type_var_map.get(tp, tp)

    origin = get_origin(tp)
    if origin:
        args = get_args(tp)
        replaced_args = tuple(_replace_typevars(arg, type_var_map) for arg in args)
        return origin[replaced_args]

    return tp


def _convert_to_class(
    data: Any, clazz: type[T], type_var_map: dict[TypeVar, type] | None = None
) -> T:
    """递归转换字典到数据类，支持泛型类型和根列表类型."""
    if type_var_map is None:
        type_var_map = {}

    origin_clazz = get_origin(clazz) or clazz

    # 处理泛型参数映射
    if get_origin(clazz):
        type_args = get_args(clazz)
        type_params = getattr(origin_clazz, "__parameters__", [])
        new_type_var_map = dict(zip(type_params, type_args, strict=False))
        type_var_map = {**type_var_map, **new_type_var_map}

    # 处理列表类型（包括根列表）
    if origin_clazz is list:
        elem_type = get_args(clazz)[0] if get_args(clazz) else Any
        elem_type = _replace_typevars(elem_type, type_var_map)
        return [_convert_to_class(e, elem_type, type_var_map) for e in data]

    # 处理数据类
    if isinstance(data, dict) and is_dataclass(origin_clazz):
        instance = origin_clazz()
        field_types = get_type_hints(origin_clazz, localns=type_var_map)

        # 确保 origin_clazz 是数据类
        if not is_dataclass(origin_clazz):
            raise TypeError(f"Expected a dataclass, got {origin_clazz}")

        for field in fields(origin_clazz):  # 现在可以安全调用 fields()
            field_name = field.name
            json_key = field.metadata.get("json_key", field_name)
            field_value = data.get(json_key, None)

            field_type = field_types.get(field_name, field.type)
            field_type = _replace_typevars(field_type, type_var_map)

            if field_value is not None:
                field_value = _convert_to_class(field_value, field_type, type_var_map)

            setattr(instance, field_name, field_value)
        return instance

    return data


def json_to_bean(json_data: str, cls: type[T]) -> T:
    """Convert JSON string to an entity class instance, with deep conversion."""
    json_dict = json.loads(json_data)
    return _convert_to_class(json_dict, cls)


def dataclass_to_dict(obj: Any, ignore_none: bool = True) -> dict:
    """将数据类转换为字典，可选忽略 None 值."""
    if not is_dataclass(obj):
        raise TypeError(f"{obj} 不是数据类实例")

    def _filter_none(data: dict) -> dict:
        """递归过滤 None 值."""
        return {
            key: _filter_none(value) if isinstance(value, dict) else value
            for key, value in data.items()
            if not (ignore_none and value is None)
        }

    return _filter_none(asdict(obj))
