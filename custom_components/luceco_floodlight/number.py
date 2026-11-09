"""Number entities for the Luceco Floodlight's settings."""

from __future__ import annotations

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.const import PERCENTAGE, EntityCategory, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import KEY_BRIGHTNESS, KEY_ON_TIME, KEY_SENSITIVITY
from .coordinator import FloodlightConfigEntry, FloodlightCoordinator
from .entity import FloodlightEntity

NUMBERS: tuple[NumberEntityDescription, ...] = (
    NumberEntityDescription(
        key=KEY_BRIGHTNESS,
        translation_key="brightness",
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        native_unit_of_measurement=PERCENTAGE,
        mode=NumberMode.SLIDER,
        entity_category=EntityCategory.CONFIG,
    ),
    NumberEntityDescription(
        key=KEY_SENSITIVITY,
        translation_key="sensitivity",
        native_min_value=0,
        native_max_value=3,
        native_step=1,
        mode=NumberMode.SLIDER,
        entity_category=EntityCategory.CONFIG,
    ),
    NumberEntityDescription(
        key=KEY_ON_TIME,
        translation_key="on_time",
        native_min_value=10,
        native_max_value=1800,
        native_step=1,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: FloodlightConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the number entities."""
    async_add_entities(
        FloodlightNumber(entry.runtime_data, entry, description)
        for description in NUMBERS
    )


class FloodlightNumber(FloodlightEntity, NumberEntity):
    """A writable setting on the floodlight."""

    def __init__(
        self,
        coordinator: FloodlightCoordinator,
        entry: FloodlightConfigEntry,
        description: NumberEntityDescription,
    ) -> None:
        """Initialize the number."""
        super().__init__(coordinator, entry, description)

    @property
    def native_value(self) -> float | None:
        """Return the value the device last reported."""
        value = self._state.get(self._key)
        return None if value is None else float(value)

    async def async_set_native_value(self, value: float) -> None:
        """Write the value to the device."""
        await self._async_write({self._key: int(value)})
