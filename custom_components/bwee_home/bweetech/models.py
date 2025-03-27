"""Models for Bwee Tech API."""

from dataclasses import dataclass


@dataclass
class User:
    """User Information."""

    username: str = None  # 用户名


@dataclass
class GatewayInfo:
    """GatewayInfo."""

    id: str = None  # 设备ID
    ip: str = None  # 设备IP地址
    mac: str = None  # 设备MAC地址
    model: str = None  # 设备型号
    name: str = None  # 设备名称
    parent_id: str = None  # 父设备ID
    parent_type: str = None  # 父设备类型
    type: str = None  # 设备类型
    version: str = None  # 设备版本


@dataclass
class PowerOn:
    """Power-on settings."""

    brightness: int = None  # 开机亮度
    brightness_mode: int = None  # 开机亮度模式
    color_cw: int = None  # 开机颜色冷暖值
    color_mode: int = None  # 开机颜色模式
    color_x: int = None  # 开机颜色X值
    color_y: int = None  # 开机颜色Y值
    mode: int = None  # 开机模式
    on: int = None  # 是否开机
    on_mode: int = None  # 开机模式


@dataclass
class ColorXY:
    """Color values."""

    x: int = None  # X坐标
    y: int = None  # Y坐标


@dataclass
class Light:
    """Device light."""

    ability: int = None  # 亮度能力
    brightness: int = None  # 亮度
    color_arr: list[ColorXY] = None  # 颜色数组
    color_cw: int = None  # 颜色冷暖值
    color_len: int = None  # 颜色数组长度
    color_mode: int = None  # 颜色模式
    color_x: int = None  # 颜色X值
    color_y: int = None  # 颜色Y值
    id: str = None  # 设备ID
    name: str = None  # 设备名称
    on: int = None  # 是否开启
    pack: list[str] = None  # 包含的设备
    position_x: int = None  # X坐标位置
    position_y: int = None  # Y坐标位置
    positions: str = None  # 位置描述
    power_on: PowerOn = None  # 开机设置
    support_segment: int = None  # 是否支持分段
    sync_status: int = None  # 同步状态
    type: str = None  # 设备类型


@dataclass
class Service:
    """Service details."""

    rid: str = None  # 资源ID
    rtype: str = None  # 资源类型


@dataclass
class Product:
    """Product details."""

    cat1_id: int = None  # 一级分类ID
    cat1_name: str = None  # 一级分类名称
    cat2_id: int = None  # 二级分类ID
    cat2_name: str = None  # 二级分类名称
    cat3_id: int = None  # 三级分类ID
    cat3_name: str = None  # 三级分类名称
    hardware_version: str = None  # 硬件版本
    manufacturer: str = None  # 制造商
    model: str = None  # 型号
    software_version: str = None  # 软件版本
    zigbee_version: str = None  # Zigbee 版本


@dataclass
class Room:
    """Room settings."""

    background: int = None  # 背景
    icon: str = None  # 房间图标
    id: str = None  # 房间ID
    name: str = None  # 房间名称
    room_kind: int = None  # 房间类别
    room_type: str = None  # 房间类型
    sequence: int = None  # 排序
    type: str = None  # 类型


@dataclass
class Device:
    """Device Information."""

    ext_light: list[Light] = None  # 设备灯光
    ext_room: Room = None  # 设备房间
    has_new: int = None  # 是否有新版本
    id: str = None  # 设备ID
    join_status: int = None  # 加入状态
    name: str = None  # 设备名称
    new_version: str = None  # 新版本
    online: int = None  # 是否在线
    product: Product = None  # 产品信息
    services: list[Service] = None  # 设备的服务列表
    type: str = None  # 设备类型


@dataclass
class DeviceUpdatePayload:
    """Device update payload."""

    id: str = None  # 设备ID
    value: dict[str, str] = None  # 值


@dataclass
class LightUpdateValue:
    """Light update value."""

    on: int = None  # 是否开启
    brightness: int = None  # 亮度
    color_arr: list[ColorXY] = None  # 颜色数组
    color_cw: int = None  # 颜色冷暖值
    color_len: int = None  # 颜色数组长度
    color_mode: int = None  # 颜色模式
    color_x: int = None  # 颜色X值
    color_y: int = None  # 颜色Y值


@dataclass
class LightUpdatePayload:
    """Light update payload."""

    device_id: str = None  # 设备ID
    id: str = None  # 光ID
    value: LightUpdateValue = None  # 修改的值


@dataclass
class Resource:
    """Resource details."""

    id: str = None  # ID
    type: str = None  # 类型

