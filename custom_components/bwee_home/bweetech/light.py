"""调用light相关接口."""

from . import API, Result
from .forms import ControlForm
from .models import Light
from .utils import dataclass_to_dict


async def get_all_lights() -> Result[Light]:
    """Get lights."""
    return await API.get("/clip/v2/resource/light", data_type=Light)


async def get_lights(device_uuid: str) -> Result[Light]:
    """Get lights."""
    return await API.get(f"/clip/v2/resource/light/{device_uuid}", data_type=Light)


async def light_by_uuid(light_uuid: str) -> Result[Light]:
    """Get lights."""
    return await API.get(f"/clip/v2/resource/light/{light_uuid}", data_type=Light)


async def light_control(light_uuid: str, form: ControlForm) -> Result:
    """Control lights."""
    return await API.put(
        f"/clip/v2/resource/light/{light_uuid}", data=dataclass_to_dict(form)
    )
