"""Models for Bwee Tech API."""

from dataclasses import dataclass

from .models import ColorXY


@dataclass
class ControlForm:
    """Light control form."""

    on: int = None
    brightness: int = None
    color_cw: int = None
    color_x: int = None
    color_y: int = None
    color_arr: list[ColorXY] = None
    name: str = None


@dataclass
class SearchForm:
    """Light control form."""

    ext_light: int = None
    ext_room: int = None
    join_status: int = 1
    cat1_id: int = None
