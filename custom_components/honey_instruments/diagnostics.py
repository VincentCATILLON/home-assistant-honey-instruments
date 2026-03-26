"""Diagnostics support for Honey Instruments."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from . import HoneyInstrumentsConfigEntry

TO_REDACT_CONFIG = {"password", "access_token", "email"}
TO_REDACT_DEVICE = {"id"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: HoneyInstrumentsConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data
    return {
        "config_entry": async_redact_data(dict(entry.data), TO_REDACT_CONFIG),
        "options": dict(entry.options),
        "devices": {
            str(device_id): {
                "device": async_redact_data(
                    device_data.get("device", {}), TO_REDACT_DEVICE
                ),
                "data_keys": list(device_data.get("data", {}).keys()),
            }
            for device_id, device_data in (coordinator.data or {}).items()
        },
    }
