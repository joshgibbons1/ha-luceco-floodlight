"""Luceco smart floodlight (Broadlink device type 0x647a), local control."""

from __future__ import annotations

from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant

from .api import FloodlightClient
from .coordinator import FloodlightConfigEntry, FloodlightCoordinator

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.LIGHT,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
]


async def async_setup_entry(hass: HomeAssistant, entry: FloodlightConfigEntry) -> bool:
    """Set up a floodlight from a config entry."""
    client = FloodlightClient(entry.data[CONF_HOST])
    coordinator = FloodlightCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: FloodlightConfigEntry) -> bool:
    """Unload a config entry and release the device's socket."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        await entry.runtime_data.client.close()
    return unloaded
