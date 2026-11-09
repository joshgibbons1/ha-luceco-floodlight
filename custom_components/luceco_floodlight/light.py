"""Light entity for the Luceco Floodlight."""

from __future__ import annotations

from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ColorMode,
    LightEntity,
    LightEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import KEY_BRIGHTNESS, KEY_LIGHT_LIT, KEY_MODE, KEY_POWER, MODE_MANUAL
from .coordinator import FloodlightConfigEntry, FloodlightCoordinator
from .entity import FloodlightEntity

LIGHT = LightEntityDescription(
    key="light", translation_key="floodlight", name=None
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: FloodlightConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the light."""
    async_add_entities([FloodlightLight(entry.runtime_data, entry)])


class FloodlightLight(FloodlightEntity, LightEntity):
    """The floodlight as a dimmable light.

    Turning it on or off uses the device's manual mode, like the vendor app's
    power button. Off therefore keeps the sensor from lighting it until another
    mode is chosen.
    """

    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}

    def __init__(
        self, coordinator: FloodlightCoordinator, entry: FloodlightConfigEntry
    ) -> None:
        """Initialize the light."""
        super().__init__(coordinator, entry, LIGHT)

    @property
    def is_on(self) -> bool:
        """Return true while the main light is lit."""
        if self._state.get(KEY_MODE) == MODE_MANUAL:
            return bool(self._state.get(KEY_POWER))
        return bool(self._state.get(KEY_LIGHT_LIT))

    @property
    def brightness(self) -> int | None:
        """Return the brightness on Home Assistant's 0-255 scale."""
        percent = self._state.get(KEY_BRIGHTNESS)
        return None if percent is None else round(percent * 255 / 100)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Switch to manual mode with the light on."""
        values = {KEY_MODE: MODE_MANUAL, KEY_POWER: 1}
        if (brightness := kwargs.get(ATTR_BRIGHTNESS)) is not None:
            values[KEY_BRIGHTNESS] = max(1, round(brightness * 100 / 255))
        await self._async_write(values)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Switch to manual mode with the light off."""
        await self._async_write({KEY_MODE: MODE_MANUAL, KEY_POWER: 0})
