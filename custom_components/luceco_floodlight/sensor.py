"""Ambient light sensor for the Luceco Floodlight."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import KEY_AMBIENT
from .coordinator import FloodlightConfigEntry, FloodlightCoordinator
from .entity import FloodlightEntity

AMBIENT_LIGHT = SensorEntityDescription(
    key=KEY_AMBIENT,
    translation_key="ambient_light_level",
    entity_category=EntityCategory.DIAGNOSTIC,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: FloodlightConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the ambient light sensor."""
    async_add_entities([FloodlightAmbientLight(entry.runtime_data, entry)])


class FloodlightAmbientLight(FloodlightEntity, SensorEntity):
    """Light level at the photocell, from 0 (night) to 3 (day)."""

    def __init__(
        self, coordinator: FloodlightCoordinator, entry: FloodlightConfigEntry
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, AMBIENT_LIGHT)

    @property
    def native_value(self) -> int | None:
        """Return the raw 0-3 level."""
        value = self._state.get(self._key)
        return None if value is None else int(value)
