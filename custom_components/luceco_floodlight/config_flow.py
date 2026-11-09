"""Config flow for the Luceco Floodlight integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST
from homeassistant.helpers.device_registry import format_mac

from .api import FloodlightClient, FloodlightError
from .const import DOMAIN, KEY_MOTION

_LOGGER = logging.getLogger(__name__)

HOST_SCHEMA = vol.Schema({vol.Required(CONF_HOST): str})


class NotAFloodlightError(Exception):
    """The device answered, but not with a floodlight's state."""


async def _async_probe(host: str) -> str:
    """Connect to the device at ``host`` and return its MAC address."""
    client = FloodlightClient(host)
    try:
        state = await client.get_state()
    finally:
        await client.close()
    if KEY_MOTION not in state or client.mac is None:
        raise NotAFloodlightError
    return client.mac


async def _async_check(host: str) -> tuple[str | None, str | None]:
    """Return (mac, None) for a working floodlight, else (None, error key)."""
    try:
        return await _async_probe(host), None
    except FloodlightError as err:
        _LOGGER.warning("Could not reach the floodlight at %s: %s", host, err)
        return None, "cannot_connect"
    except NotAFloodlightError:
        return None, "unsupported"


class FloodlightConfigFlow(ConfigFlow, domain=DOMAIN):
    """Add a floodlight by IP address."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Ask for the floodlight's IP address."""
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST]
            mac, error = await _async_check(host)
            if mac is not None:
                await self.async_set_unique_id(format_mac(mac))
                self._abort_if_unique_id_configured(updates={CONF_HOST: host})
                return self.async_create_entry(
                    title="Luceco Floodlight", data={CONF_HOST: host}
                )
            errors["base"] = error or "cannot_connect"
        return self.async_show_form(
            step_id="user", data_schema=HOST_SCHEMA, errors=errors
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Change the floodlight's IP address."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST]
            mac, error = await _async_check(host)
            if mac is not None:
                await self.async_set_unique_id(format_mac(mac))
                self._abort_if_unique_id_mismatch(reason="wrong_device")
                return self.async_update_reload_and_abort(
                    entry, data_updates={CONF_HOST: host}
                )
            errors["base"] = error or "cannot_connect"
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(HOST_SCHEMA, entry.data),
            errors=errors,
        )
