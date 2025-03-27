"""调用light相关接口."""

from . import API, Result
from .forms import ControlForm, SearchForm
from .models import Device
from .utils import dataclass_to_dict


async def get_all_devices(form: SearchForm) -> Result[Device]:
    """Get devices."""
    return await API.get(
        "/clip/v2/resource/device", params=dataclass_to_dict(form), data_type=Device
    )


async def device_by_uuid(device_uuid: str) -> Result[Device]:
    """Get devices."""
    return await API.get(f"/clip/v2/resource/device/{device_uuid}", data_type=Device)


async def device_control(device_uuid: str, form: ControlForm) -> Result:
    """Control devices."""
    return await API.put(
        f"/clip/v2/resource/device/{device_uuid}/light", data=dataclass_to_dict(form)
    )
