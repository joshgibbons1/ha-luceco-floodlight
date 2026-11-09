"""Motion sensor for the Luceco Floodlight."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import KEY_MOTION
from .coordinator import FloodlightConfigEntry, FloodlightCoordinator
from .entity import FloodlightEntity

MOTION = BinarySensorEntityDescription(
    key=KEY_MOTION,
    translation_key="motion",
    device_class=BinarySensorDeviceClass.MOTION,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: FloodlightConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the motion sensor."""
    async_add_entities([FloodlightMotion(entry.runtime_data, entry)])


class FloodlightMotion(FloodlightEntity, BinarySensorEntity):
    """PIR trigger, held for the on time and only active in low light."""

    def __init__(
        self, coordinator: FloodlightCoordinator, entry: FloodlightConfigEntry
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, MOTION)

    @property
    def is_on(self) -> bool:
        """Return true while the PIR flag is set."""
        return bool(self._state.get(self._key))
