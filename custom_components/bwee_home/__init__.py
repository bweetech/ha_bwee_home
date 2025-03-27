"""The BWEE home integration."""

from __future__ import annotations

import logging

from .light import DeviceManager
from homeassistant.core import HomeAssistant

from .bweetech import API
from .config_flow import BweeConfigFlow
from .const import DOMAIN, SUPPORT_PLATFORMS

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up BWEE home."""
    _LOGGER.info("Starting Bwee Home integration")
    hass.data.setdefault(DOMAIN, {})
    # {[entry_id:str]: list[BWEEDevice]}
    hass.data[DOMAIN].setdefault("devices", {})
    # {[entry_id:str]: entities}
    hass.data[DOMAIN].setdefault("entities", {})
    for platform in SUPPORT_PLATFORMS:
        hass.data[DOMAIN]["entities"][platform] = []
    # 初始化API
    await API.init_session()
    return True


async def async_shutdown(hass: HomeAssistant) -> None:
    """Shutdown BWEE home."""
    _LOGGER.info("Shutdown Bwee Home integration")
    await API.close_session()


async def async_setup_entry(hass: HomeAssistant, config_entry: BweeConfigFlow) -> bool:
    """Set up BWEE home from a config entry."""
    _LOGGER.info("Setup Bwee Home entry")
    hass.data.setdefault(DOMAIN, {})
    # {[lights:Light]: list[Light]}
    hass.data[DOMAIN].setdefault("devices", {})
    # {[gateway:GatewayInfo]: gateways}
    hass.data[DOMAIN].setdefault("gateways", {})
    # {dm:DeviceManager}
    hass.data[DOMAIN].setdefault("dm", None)
    for platform in SUPPORT_PLATFORMS:
        hass.data[DOMAIN]["entities"][platform] = []
    await hass.config_entries.async_forward_entry_setups(
        config_entry, SUPPORT_PLATFORMS
    )
    return True


async def async_unload_entry(hass: HomeAssistant, _: BweeConfigFlow) -> bool:
    """Unload a config entry."""
    _LOGGER.info("Unload Bwee Home entry")
    # 清空设备
    dm: DeviceManager = hass.data[DOMAIN]["dm"]
    if dm:
        await dm.close()
        hass.data[DOMAIN]["dm"] = None
    await API.close_session()
    return True
