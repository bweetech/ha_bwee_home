"""Platform for light integration."""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP_KELVIN,
    ATTR_XY_COLOR,
    PLATFORM_SCHEMA as LIGHT_PLATFORM_SCHEMA,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_IP_ADDRESS
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.color import brightness_to_value, value_to_brightness

from .bweetech import API
from .bweetech.device import device_control, get_all_devices
from .bweetech.enums import DeviceSupport
from .bweetech.forms import ControlForm, SearchForm
from .bweetech.light import get_lights
from .bweetech.models import Device, DeviceUpdatePayload, LightUpdatePayload, Resource
from .bweetech.mqtt_client import MqttServiceForGateway
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
LIGHT_PLATFORM_SCHEMA = LIGHT_PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_IP_ADDRESS): cv.string,
        vol.Optional(CONF_API_KEY): cv.string,
    }
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the device platform from a config entry."""
    # 获取配置条目中的数据
    ip_address = config_entry.data.get(CONF_IP_ADDRESS)
    api_key = config_entry.data.get(CONF_API_KEY)
    _LOGGER.info("Setting up device platform with IP address: %s", ip_address)

    # 配置API
    API.init_gateway_info(ip_address, api_key)

    # 创建设备管理员
    if hass.data[DOMAIN]["dm"] is None:
        dm = DeviceManager(hass, async_add_entities, ip_address)
        await dm.init_devices()
        hass.data[DOMAIN]["dm"] = dm    

    await API.close_session()
    return True

class BweeLight(LightEntity):
    """Representation of an Awesome Light."""

    def __init__(self, id: str) -> None:
        """Initialize the device."""
        self._id = id
        self._attr_unique_id = id

    @property
    def supported_color_modes(self):
        """Return the supported color_mode of the device."""
        if "devices" in self.hass.data[DOMAIN]:
            devices: dict[str, Device] = self.hass.data[DOMAIN]["devices"]
            gp_id = devices.get(self._id).product.cat3_id
            support = DeviceSupport.of_gp_id(gp_id=gp_id)
            if support == DeviceSupport.RGB_CW:
                return (ColorMode.COLOR_TEMP,ColorMode.XY,)
            if support == DeviceSupport.RGB:
                return (ColorMode.XY,)
            if support == DeviceSupport.CW:
                return (ColorMode.COLOR_TEMP,)
        return (ColorMode.UNKNOWN,)

    @property
    def color_mode(self):
        """Return the color_mode of the device."""
        if "devices" in self.hass.data[DOMAIN]:
            devices: dict[str, Device] = self.hass.data[DOMAIN]["devices"]
            color_mode = devices.get(self._id).ext_light[0].color_mode
            if color_mode == 1:
                return ColorMode.XY
            if color_mode == 2:
                return ColorMode.COLOR_TEMP
            return ColorMode.UNKNOWN
        return None

    @property
    def name(self):
        """Return the name of the device."""
        if "devices" in self.hass.data[DOMAIN]:
            devices: dict[str, Device] = self.hass.data[DOMAIN]["devices"]
            return devices.get(self._id).name
        return None

    @property
    def available(self):
        """Return the available of the device."""
        if "devices" in self.hass.data[DOMAIN]:
            devices: dict[str, Device] = self.hass.data[DOMAIN]["devices"]
            return devices.get(self._id).online
        return None

    @property
    def is_on(self):
        """Return true if the light is on."""
        if "devices" in self.hass.data[DOMAIN]:
            devices: dict[str, Device] = self.hass.data[DOMAIN]["devices"]
            return devices.get(self._id).ext_light[0].on == 1
        return None

    @property
    def brightness(self):
        """Return the brightness of the device."""
        if "devices" in self.hass.data[DOMAIN]:
            devices: dict[str, Device] = self.hass.data[DOMAIN]["devices"]
            return value_to_brightness(
                (
                    1,
                    100,
                ),
                devices.get(self._id).ext_light[0].brightness,
            )
        return None

    @property
    def color_temp_kelvin(self):
        """Return the color_temp_kelvin of the device."""
        if "devices" in self.hass.data[DOMAIN]:
            devices: dict[str, Device] = self.hass.data[DOMAIN]["devices"]
            return devices.get(self._id).ext_light[0].color_cw
        return None

    @property
    def min_color_temp_kelvin(self) -> int:
        """Set min mireds."""
        return 2000

    @property
    def max_color_temp_kelvin(self) -> int:
        """Set max mireds."""
        return 6500

    @property
    def xy_color(self):
        """Return the color_temp_kelvin of the device."""
        if "devices" in self.hass.data[DOMAIN]:
            devices: dict[str, Device] = self.hass.data[DOMAIN]["devices"]
            x = devices.get(self._id).ext_light[0].color_x / 65535
            y = devices.get(self._id).ext_light[0].color_y / 65535
            return (
                x,
                y,
            )
        return None

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        if "devices" in self.hass.data[DOMAIN]:
            devices: dict[str, Device] = self.hass.data[DOMAIN]["devices"]
            device = devices.get(self._id)
            return DeviceInfo(
                identifiers={
                    # Serial numbers are unique identifiers within a specific domain
                    (DOMAIN, self._id)
                },
                name=device.name,
                manufacturer=device.product.manufacturer,
                model=device.product.cat3_name,
                model_id=device.product.model,
                sw_version=device.product.software_version,
                hw_version=device.product.hardware_version,
                translation_key=device.name,
                suggested_area=device.ext_room.name,
                via_device=(DOMAIN, device.id),
            )

    async def async_turn_on(self, **kwargs):
        """Turn the light on."""

        # on
        form = ControlForm(on=1)
        # brightness
        if ATTR_BRIGHTNESS in kwargs:
            brightness = int(
                brightness_to_value(
                    (
                        1,
                        100,
                    ),
                    kwargs[ATTR_BRIGHTNESS],
                )
            )
            form.brightness = brightness
        # color-temperature
        if ATTR_COLOR_TEMP_KELVIN in kwargs:
            form.color_cw = kwargs[ATTR_COLOR_TEMP_KELVIN]
        # rgb color
        if ATTR_XY_COLOR in kwargs:
            x = kwargs[ATTR_XY_COLOR][0]
            y = kwargs[ATTR_XY_COLOR][1]
            form.color_x = int(x * 65535)
            form.color_y = int(y * 65535)
        res = await device_control(self._id, form)
        _LOGGER.info("Turn_on: form:%s,res:%s", form, res)
        if "devices" in self.hass.data[DOMAIN]:
            devices: dict[str, Device] = self.hass.data[DOMAIN]["devices"]
            light = devices.get(self._id).ext_light[0]
            if form.brightness:
                light.brightness = form.brightness
            if form.color_cw:
                light.color_cw = form.color_cw
            if form.color_x:
                light.color_x = form.color_x
            if form.color_y:
                light.color_y = form.color_y
            light.on = 1

    async def async_turn_off(self, **kwargs):
        """Turn the light off."""
        form = ControlForm(on=0)
        res = await device_control(self._id, form)
        _LOGGER.debug("Turn_off: form:%s,res:%s", form, res)
        if "devices" in self.hass.data[DOMAIN]:
            devices: dict[str, Device] = self.hass.data[DOMAIN]["devices"]
            devices.get(self._id).ext_light[0].on = 0


class DeviceManager:
    """Device manager tool."""

    _hass: HomeAssistant
    _async_add_entities: AddEntitiesCallback
    _light_entitie_dict: dict[str, BweeLight]
    _mqtt_service: MqttServiceForGateway

    def __init__(
        self,
        hass: HomeAssistant,
        async_add_entities: AddEntitiesCallback,
        ip_address: str,
    ) -> None:
        """Init device manager tool."""
        self._hass = hass
        self._async_add_entities = async_add_entities
        self._light_entitie_dict = {}
        self._mqtt_service = MqttServiceForGateway(ip_address)
        self._mqtt_service.on_device_add = self.on_device_add
        self._mqtt_service.on_device_remove = self.on_device_remove
        self._mqtt_service.on_device_update = self.on_device_update
        self._mqtt_service.on_light_update = self.on_light_update

    @staticmethod
    def to_dict(devices: list[Device]) -> dict[str, Device]:
        """Lights to dict."""
        result = {}
        for device in devices:
            device_id = device.id
            result[device_id] = device
        return result

    async def init_devices(self) -> None:
        """Get devices."""
        form = SearchForm(cat1_id=2, ext_light=1, ext_room=1)
        res = await get_all_devices(form)
        if res.is_ok():
            self._hass.data[DOMAIN]["devices"] = self.to_dict(res.data.arr)
        # 清空
        if len(self._light_entitie_dict) > 0:
            for light in self._light_entitie_dict.values():
                light.async_remove()
            self._light_entitie_dict.clear()
        # 创建灯的实体
        devices: dict[str, Device] = self._hass.data[DOMAIN]["devices"]
        self.init_light_entities(devices.values())

        # 连接MQTT
        self._mqtt_service.connect()

    def init_light_entities(self, devices: list[Device]) -> None:
        """Create light entitie."""
        for device in devices:
            light = BweeLight(device.id)
            self._light_entitie_dict.setdefault(device.id, light)
        self._async_add_entities(self._light_entitie_dict.values())

    async def create_light_entitie(self, device: Device) -> None:
        """Create light entitie."""
        light = BweeLight(device.id)
        self._light_entitie_dict.setdefault(device.id, light)
        devices: dict[str, Device] = self._hass.data[DOMAIN]["devices"]
        if not device.ext_light:
            # 查询ext_light
            res = await get_lights(device_uuid=device.id)
            if res.is_ok():
                device.ext_light = res.data.arr
        devices.setdefault(device.id, device)
        self._async_add_entities([light])

    async def remove_light_entitie(self, device_id: str) -> None:
        """Remove light entitie."""
        light = self._light_entitie_dict.pop(device_id)
        if light:
            devices: dict[str, Device] = self._hass.data[DOMAIN]["devices"]
            devices.pop(device_id)
            await light.async_remove()
    
    async def clear_light_entitie(self) -> None:
        """Remove light entitie."""
        devices: dict[str, Device] = self._hass.data[DOMAIN]["devices"]
        device_ids = list(devices.keys())
        for device_id in device_ids:
            await self.remove_light_entitie(device_id)

    async def on_device_add(self, data: list[Device]):
        """设备新增时触发."""
        for device in data:
            await self.create_light_entitie(device)

    async def on_device_remove(self, data: list[Resource]):
        """设备删除时触发."""
        for service in data:
            await self.remove_light_entitie(service.id)

    async def on_device_update(self, data: list[DeviceUpdatePayload]):
        """设备更新时触发."""
        for item in data:
            entitie = self._light_entitie_dict.get(item.id)
            devices: dict[str, Device] = self._hass.data[DOMAIN]["devices"]
            device = devices.get(item.id)
            if entitie and device:
                if "name" in item.value:
                    device.name = item.value.get("name")
                await entitie.async_write_ha_state()

    async def on_light_update(self, data: list[LightUpdatePayload]):
        """灯光更新时触发."""
        for item in data:
            entitie = self._light_entitie_dict.get(item.device_id)
            devices: dict[str, Device] = self._hass.data[DOMAIN]["devices"]
            device = devices.get(item.device_id)
            if entitie and device and device.ext_light[0].id == item.id:
                if item.value.brightness is not None:
                    device.ext_light[0].brightness = item.value.brightness
                if item.value.color_cw is not None:
                    device.ext_light[0].color_cw = item.value.color_cw
                if item.value.color_arr is not None:
                    device.ext_light[0].color_arr = item.value.color_arr
                if item.value.color_x is not None:
                    device.ext_light[0].color_x = item.value.color_x
                if item.value.color_y is not None:
                    device.ext_light[0].color_y = item.value.color_y
                if item.value.on is not None:
                    device.ext_light[0].on = item.value.on
                if item.value.color_mode is not None:
                    device.ext_light[0].color_mode = item.value.color_mode
                await entitie.async_write_ha_state()

    async def close(self):
        await self.clear_light_entitie()
        self._mqtt_service.disconnect()
