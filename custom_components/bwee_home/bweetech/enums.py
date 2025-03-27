"""Bwee enums."""

from enum import Enum


class DeviceSupport(Enum):
    """设备支持的功能枚举类."""

    NONE = 0  # 什么都不支持
    ON_OFF = 1  # 支持开关灯
    BRIGHT = 2  # 支持调亮度
    CW = 3  # 支持调色温
    RGB = 4  # 支持调颜色
    RGB_CW = 5  # 支持调色温和颜色

    @property
    def support_code(self) -> int:
        """获取支持的功能代码."""
        return self.value

    @staticmethod
    def of_gp_id(gp_id: int | None) -> "DeviceSupport":
        """根据 gpId 获取对应的设备支持功能."""
        if gp_id is not None:
            support = (gp_id // 100) % 10
            for device_support in DeviceSupport:
                if device_support.support_code == support:
                    return device_support
        return DeviceSupport.NONE
