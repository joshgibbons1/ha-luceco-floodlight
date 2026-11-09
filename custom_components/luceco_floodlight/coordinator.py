"""Polling coordinator for the Luceco smart floodlight."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import FloodlightClient, FloodlightError
from .const import DOMAIN, SCAN_INTERVAL_SECONDS

_LOGGER = logging.getLogger(__name__)


class FloodlightCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Poll the floodlight's state."""

    config_entry: FloodlightConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        entry: FloodlightConfigEntry,
        client: FloodlightClient,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL_SECONDS),
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.client.get_state()
        except FloodlightError as err:
            raise UpdateFailed(str(err)) from err


type FloodlightConfigEntry = ConfigEntry[FloodlightCoordinator]
