"""DataUpdateCoordinator for Honey Instruments."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    HoneyInstrumentsApi,
    HoneyInstrumentsApiError,
    HoneyInstrumentsAuthError,
)
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, LOGGER


class HoneyInstrumentsCoordinator(DataUpdateCoordinator[dict[int, dict[str, Any]]]):
    """Class to manage fetching data from the Honey Instruments API."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: HoneyInstrumentsApi,
        scan_interval: int = DEFAULT_SCAN_INTERVAL,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.api = api

    async def _async_update_data(self) -> dict[int, dict[str, Any]]:
        """Fetch all devices then latest data for each device."""
        try:
            devices = await self.api.get_devices()
        except HoneyInstrumentsAuthError as err:
            raise ConfigEntryAuthFailed(f"Authentication failed: {err}") from err
        except HoneyInstrumentsApiError as err:
            raise UpdateFailed(f"Error fetching devices: {err}") from err

        result: dict[int, dict[str, Any]] = {}

        for device in devices:
            device_id: int = device["id"]
            try:
                messages = await self.api.get_device_data(device_id)
                latest = messages[0] if messages else {}
            except HoneyInstrumentsAuthError as err:
                raise ConfigEntryAuthFailed(f"Authentication failed: {err}") from err
            except (HoneyInstrumentsApiError, IndexError, KeyError) as err:
                LOGGER.warning("Failed to fetch data for device %s: %s", device_id, err)
                latest = {}

            result[device_id] = {
                "device": device,
                "data": latest,
            }

        return result
