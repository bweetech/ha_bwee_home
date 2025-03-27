"""Constants for the BWEE home integration."""

from homeassistant.const import Platform

DOMAIN = "bwee_home"

SUPPORT_PLATFORMS: list[Platform] = [
    Platform.LIGHT
    # Platform.BUTTON,
    # Platform.SCENE,
    # Platform.SWITCH,
]
