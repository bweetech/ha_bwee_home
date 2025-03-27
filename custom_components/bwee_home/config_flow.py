"""Config flow for BWEE Home integration."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import ping3
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_API_KEY, CONF_IP_ADDRESS
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo

from .bweetech import API
from .bweetech.gateway import get_gateway_info, get_auth
from .bweetech.utils.gateway_discovery import GatewayDiscovery
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_IP_ADDRESS): str,
        vol.Optional(CONF_API_KEY): str,
    }
)


class BweeConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for BWEE home."""

    VERSION = 1
    MINOR_VERSION = 0

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._task_get_api_key: asyncio.Task[None] = None
        self._gateway_ip: str = None
        self._gateway_api_key: str = None
        self._gateway_mac: str = None

    async def async_step_zeroconf(
        self, discovery_info: ZeroconfServiceInfo
    ) -> ConfigFlowResult:
        """Handle a discovered Bwee gateway."""
        if "Bwee Bridge" not in discovery_info.name:
            return self.async_abort(reason="invalid_device")
        # Ignore if host is IPv6
        if discovery_info.ip_address.version == 6:
            return self.async_abort(reason="invalid_host")
        
        gateway_mac = discovery_info.properties['id']
        await self.async_set_unique_id(gateway_mac)
        self._abort_if_unique_id_configured(
            updates={CONF_IP_ADDRESS: discovery_info.host}, reload_on_update=True
        )
        
        self._gateway_ip = discovery_info.host
        return await self.async_step_linkage()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        return await self.async_step_init(user_input)

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        # if user_input is None:
        #     # 搜索当前局域网中是否存在网关设备（持续5秒）
        #     response = self._gateway_discovery.discovery(5)
        #     if response is not None:
        #         # 显示连接弹框
        #         self._gateway_ip = response.data.ip
        #         return await self.async_step_linkage(user_input)
        # 显示手动搜索输入框
        return await self.async_step_manual(user_input)

    async def async_step_manual(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the manual step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                done = await self.validate_input(user_input)
                self._gateway_ip = user_input.get(CONF_IP_ADDRESS)
                self._gateway_api_key = user_input.get(CONF_API_KEY)
                if done:
                    return await self.async_step_done(user_input)
                return await self.async_step_linkage()
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except DeviceDiscoveryError:
                errors["base"] = "device_not_found"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
        # 显示手动搜索输入框
        return self.async_show_form(
            step_id="manual", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_linkage(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the linkage step."""
        if user_input is None:
            return self.async_show_form(step_id="linkage")

        error = None
        if self._gateway_ip:
            res = await get_auth(self._gateway_ip)
            if res.is_ok():
                self._gateway_api_key = res.data.obj.username
                return await self.async_step_done(user_input)
            if res.code == -10086:
                error = "cannot_connect"
            else:
                error = "no_tap_button"
        return self.async_show_form(step_id="linkage", errors={"base": error})

    async def async_step_done(
        self, _: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """配置步骤完成，返回实体."""
        if self._gateway_mac is None:
            # 获取设备Id
            API.init_gateway_info(self._gateway_ip, self._gateway_api_key)
            res = await get_gateway_info()
            if res.is_ok() and self.unique_id is None:
                gateway_info = res.data.arr[0]
                self._gateway_mac = gateway_info.mac
        
        if self._gateway_mac:
            await self.async_set_unique_id(
                self._gateway_mac, raise_on_progress=False
            )
        
        return self.async_create_entry(
            title=f"BWEE Bridge {self._gateway_ip}",
            data={
                CONF_IP_ADDRESS: self._gateway_ip,
                CONF_API_KEY: self._gateway_api_key,
            },
        )

    async def validate_input(self: BweeConfigFlow, user_input: dict[str, Any]) -> bool:
        """Validate the user input allows us to connect."""
        # 检查输入的IP地址是否正确
        ping_result = ping3.ping(user_input[CONF_IP_ADDRESS], 2)
        if ping_result is None:
            raise DeviceDiscoveryError("device_not_found")

        # 检查输入的密码是否正确
        if CONF_API_KEY in user_input and user_input[CONF_API_KEY] is not None:
            API.init_gateway_info(user_input[CONF_IP_ADDRESS], user_input[CONF_API_KEY])
            response = await get_gateway_info()
            if response.code == -10086:
                raise CannotConnect("cannot_connect")
            if not response.is_ok():
                raise InvalidAuth("invalid_auth")
            self._gateway_mac = response.data.arr[0].mac
            return True
        return False


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


class DeviceDiscoveryError(HomeAssistantError):
    """Error to indicate device could not be discovered."""
