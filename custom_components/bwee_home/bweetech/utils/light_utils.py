"""Light util."""

LIGHT_POWER = 1
LIGHT_BRIGHT = 2
LIGHT_CW = 4
LIGHT_COLOR = 8
LIGHT_SEGMENT = 10


def _is_support(ability: int, support_code: int):
    """Check support."""
    return (ability & support_code) == support_code


def is_support_power(ability: int):
    """Check support power."""
    return _is_support(ability, LIGHT_POWER)


def is_support_bright(ability: int):
    """Check support bright."""
    return _is_support(ability, LIGHT_BRIGHT)


def is_support_cw(ability: int):
    """Check support cw."""
    return _is_support(ability, LIGHT_CW)


def is_support_color(ability: int):
    """Check support color."""
    return _is_support(ability, LIGHT_COLOR)


def is_support_segment(ability: int):
    """Check support segment."""
    return _is_support(ability, LIGHT_SEGMENT)
