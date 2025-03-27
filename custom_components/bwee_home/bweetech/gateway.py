"""调用网关本身的接口."""

from . import API, Result
from .models import GatewayInfo, User


async def get_auth(gateway_ip) -> Result[User]:
    """Get gateway auth info."""
    return await API.send_request(
        "POST",
        f"http://{gateway_ip}:8080",
        "/api",
        None,
        {"device_type": "bweetech#home_assistant"},
        data_type=User,
    )


async def get_gateway_info() -> Result[GatewayInfo]:
    """Get gateway info."""
    return await API.get("/clip/v2/resource/bridge", data_type=GatewayInfo)
