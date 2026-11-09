"""Local client for the Luceco smart floodlight (Broadlink device type 0x647a)."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
import contextlib
import importlib
import logging
from typing import Any

import broadlink_async as broadlink

_LOGGER = logging.getLogger(__name__)

_COMMAND_JSON = 0x6A
_FLAG_WRITE = 2


def _load_bulb_class() -> type:
    """Return the library's light bulb class.

    The floodlight is missing from the library's device table, but it speaks
    the same JSON protocol as the bulbs, so that class is borrowed for it.
    """
    bulb = getattr(broadlink, "lb1", None)
    if bulb is None:
        bulb = importlib.import_module(f"{broadlink.__name__}.light").lb1
    return bulb


_Bulb = _load_bulb_class()


class FloodlightError(Exception):
    """The floodlight could not be reached or rejected a request."""


async def _close(device: Any) -> None:
    """Release a device's UDP socket."""
    close = getattr(device, "aclose", None)
    if close is not None:
        with contextlib.suppress(Exception):
            await close()


class FloodlightClient:
    """Reads and writes the floodlight's JSON state over the local network."""

    def __init__(self, host: str) -> None:
        """Initialize the client."""
        self.host = host
        self.mac: str | None = None
        self._device: Any = None
        self._lock = asyncio.Lock()

    async def get_state(self) -> dict[str, Any]:
        """Return the device's full state."""
        return await self._run(lambda device: device.get_state())

    async def set_values(self, values: dict[str, int]) -> None:
        """Write one or more keys to the device."""

        async def write(device: Any) -> None:
            # The bulb class has no public call for arbitrary keys.
            packet = device._encode(_FLAG_WRITE, values)  # noqa: SLF001
            await device.send_packet(_COMMAND_JSON, packet)

        await self._run(write)

    async def close(self) -> None:
        """Close the connection."""
        async with self._lock:
            await self._drop_device()

    async def _connect(self) -> Any:
        probe = await broadlink.hello(self.host)
        try:
            device = _Bulb(
                probe.host,
                probe.mac,
                probe.devtype,
                name=probe.name,
                is_locked=probe.is_locked,
            )
            mac = probe.mac
            self.mac = mac.hex() if isinstance(mac, (bytes, bytearray)) else str(mac)
        finally:
            await _close(probe)
        try:
            await device.auth()
        except Exception:
            await _close(device)
            raise
        return device

    async def _drop_device(self) -> None:
        device, self._device = self._device, None
        if device is not None:
            await _close(device)

    async def _run(self, operation: Callable[[Any], Awaitable[Any]]) -> Any:
        """Run an operation, reconnecting once if the connection went stale."""
        async with self._lock:
            error: Exception | None = None
            for _ in range(2):
                try:
                    if self._device is None:
                        self._device = await self._connect()
                    return await operation(self._device)
                except Exception as err:  # noqa: BLE001
                    error = err
                    await self._drop_device()
            raise FloodlightError(
                f"Cannot talk to the floodlight at {self.host}: {error!r}"
            ) from error
