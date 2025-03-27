"""Api client for BweeTech API."""

import logging
import platform
import sys
from typing import Any, TypeVar

import aiohttp

from .api_models import Result, parse_result
from .const import REQUEST_TIMEOUT

# 日志设置
_LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
# 泛型
T = TypeVar("T")


class ApiClient:
    """Client for BweeTech API."""

    def __init__(self) -> None:
        """Initialize the."""
        self._session: aiohttp.ClientSession | None = None
        self._user_agent: str | None = None
        self.gateway_host = ""
        self.api_key = ""

    async def init_session(self) -> None:
        """Initialize the aiohttp session for the bwee_home integration."""
        if self._session is None:
            self._session = aiohttp.ClientSession()
        self.init_user_agent()
        self.init_api_auth()

    async def close_session(self) -> None:
        """Close the aiohttp."""
        if self._session:
            await self._session.close()
            self._session = None

    def init_user_agent(self) -> None:
        """Generate User-Agent for the bwee_home integration."""
        python_version = sys.version.split(" ", maxsplit=1)[0]
        platform_info = platform.system() + " " + platform.release()
        user_agent = (
            f"bwee_home/1.0 (Home Assistant; Python/{python_version}; {platform_info})"
        )
        if self._session:
            self._session.headers.update({"User-Agent": user_agent})

    def init_api_auth(self):
        """Get the username from the config."""
        if self._session:
            self._session.headers.update({"application-key": self.api_key})

    def init_gateway_info(
        self, ip_address: str, api_key: str, port: int = 8080, protocol: str = "http"
    ) -> None:
        """Set the gateway_ip and api_key."""
        self.gateway_host = f"{protocol}://{ip_address}:{port}"
        self.api_key = api_key
        self.init_api_auth()

    async def send_request(
        self,
        method: str,
        host: str,
        url: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        data_type: type[T] = dict,
    ) -> Result[T]:
        """Send a request to the API."""
        if self._session is None:
            await self.init_session()
        params = params if params is not None else {}
        data = data if data is not None else {}
        headers = headers if headers is not None else {}
        for key in self._session.headers:
            headers.setdefault(key, self._session.headers.get(key))
        try:
            full_url = host + url
            async with self._session.request(
                method,
                full_url,
                params=params,
                json=data,
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            ) as response:
                # If the response is successful
                response_data = await response.text()  # Assuming the API returns JSON
                status_code = response.status

                _LOGGER.info(
                    "Http Request:%s,params:%s,data:%s,headers:%s", full_url, params, data, headers
                )

                # Create Result object based on response status and data
                if response.status == 200:
                    _LOGGER.debug("Http Response:%s", response_data)
                    return parse_result(response_data, data_type)
                if response.status == 400:
                    return await self.send_request(method, host, url, params, data, headers, data_type)
                return self.handle_aiohttp_error(
                    method, url, f"Response code: {status_code}"
                )
        except aiohttp.ClientResponseError as e:
            return self.handle_aiohttp_error(method, url, str(e))
        except aiohttp.ClientConnectionError as e:
            return self.handle_aiohttp_error(method, url, str(e))
        except aiohttp.ClientError as e:
            return self.handle_aiohttp_error(method, url, str(e))
        except TimeoutError as e:
            return self.handle_aiohttp_error(method, url, str(e))

    @staticmethod
    def handle_aiohttp_error(method: str, url: str, message: str) -> Result[T]:
        """Handle and log aiohttp errors, return a Result object."""
        _LOGGER.error("Error while sending %s request to %s: %s", method, url, message)
        return Result(code=-10086, msg=message)

    async def get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
        data_type: type[T] = dict,
    ) -> Result[T]:
        """Send a GET request."""
        return await self.send_request(
            "GET",
            self.gateway_host,
            url,
            params=params,
            headers=headers,
            data_type=data_type,
        )

    async def post(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
        data_type: type[T] = dict,
    ) -> Result[T]:
        """Send a POST request."""
        return await self.send_request(
            "POST",
            self.gateway_host,
            url,
            data=data,
            headers=headers,
            data_type=data_type,
        )

    async def put(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
        data_type: type[T] = dict,
    ) -> Result[T]:
        """Send a PUT request."""
        return await self.send_request(
            "PUT",
            self.gateway_host,
            url,
            data=data,
            headers=headers,
            data_type=data_type,
        )

    async def delete(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
        data_type: type[T] = dict,
    ) -> Result[T]:
        """Send a DELETE request."""
        return await self.send_request(
            "DELETE",
            self.gateway_host,
            url,
            params=params,
            headers=headers,
            data_type=data_type,
        )
