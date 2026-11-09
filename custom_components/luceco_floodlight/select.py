"""Select entities for the Luceco Floodlight: mode and sensor light level."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import (
    KEY_LIGHT_LEVEL,
    KEY_MODE,
    LEVEL_DAY,
    LEVEL_DUSK,
    LEVEL_NIGHT,
    MODE_DUSK_TO_DAWN,
    MODE_MANUAL,
    MODE_NIGHT_GLOW,
    MODE_SENSOR,
)
from .coordinator import FloodlightConfigEntry, FloodlightCoordinator
from .entity import FloodlightEntity


@dataclass(frozen=True, kw_only=True)
class FloodlightSelectDescription(SelectEntityDescription):
    """Describe a select that maps option names to device values."""

    values: dict[str, int]


SELECTS: tuple[FloodlightSelectDescription, ...] = (
    FloodlightSelectDescription(
        key=KEY_MODE,
        translation_key="mode",
        values={
            "sensor": MODE_SENSOR,
            "manual": MODE_MANUAL,
            "dusk_to_dawn": MODE_DUSK_TO_DAWN,
            "night_glow": MODE_NIGHT_GLOW,
        },
    ),
    FloodlightSelectDescription(
        key=KEY_LIGHT_LEVEL,
        translation_key="sensor_active_when",
        entity_category=EntityCategory.CONFIG,
        values={
            "night": LEVEL_NIGHT,
            "dusk": LEVEL_DUSK,
            "day": LEVEL_DAY,
        },
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: FloodlightConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the select entities."""
    async_add_entities(
        FloodlightSelect(entry.runtime_data, entry, description)
        for description in SELECTS
    )


class FloodlightSelect(FloodlightEntity, SelectEntity):
    """Map a numeric device value to named options."""

    entity_description: FloodlightSelectDescription

    def __init__(
        self,
        coordinator: FloodlightCoordinator,
        entry: FloodlightConfigEntry,
        description: FloodlightSelectDescription,
    ) -> None:
        """Initialize the select."""
        super().__init__(coordinator, entry, description)
        self._attr_options = list(description.values)

    @property
    def current_option(self) -> str | None:
        """Return the option matching the device's value, if any."""
        value = self._state.get(self._key)
        for option, number in self.entity_description.values.items():
            if number == value:
                return option
        return None

    async def async_select_option(self, option: str) -> None:
        """Write the chosen option to the device."""
        await self._async_write({self._key: self.entity_description.values[option]})
