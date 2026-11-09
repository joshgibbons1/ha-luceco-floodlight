"""Base entity for the Luceco Floodlight integration."""

from __future__ import annotations

from typing import Any

from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import FloodlightError
from .const import DOMAIN
from .coordinator import FloodlightConfigEntry, FloodlightCoordinator


class FloodlightEntity(CoordinatorEntity[FloodlightCoordinator]):
    """An entity backed by the floodlight's polled state."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: FloodlightCoordinator,
        entry: FloodlightConfigEntry,
        description: EntityDescription,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._key = description.key
        device_id = entry.unique_id or entry.entry_id
        slug = description.key.replace(" ", "_").lower()
        self._attr_unique_id = f"{device_id}_{slug}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name="Luceco Floodlight",
            manufacturer="Luceco",
            model="Smart PIR Floodlight (0x647a)",
        )

    @property
    def _state(self) -> dict[str, Any]:
        """Return the last polled device state."""
        return self.coordinator.data

    async def _async_write(self, values: dict[str, int]) -> None:
        """Write keys to the device, then refresh the state."""
        try:
            await self.coordinator.client.set_values(values)
        except FloodlightError as err:
            raise HomeAssistantError(str(err)) from err
        await self.coordinator.async_request_refresh()
