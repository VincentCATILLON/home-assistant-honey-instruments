"""Custom integration to integrate Honey Instruments with Home Assistant.

For more details about this integration, please refer to
https://cloud.honeyinstruments.com/doc/README_REST_API.pdf
"""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import HoneyInstrumentsApi
from .const import (
    CONF_ACCESS_TOKEN,
    CONF_EMAIL,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    LOGGER,
    PLATFORMS,
)
from .coordinator import HoneyInstrumentsCoordinator

type HoneyInstrumentsConfigEntry = ConfigEntry[HoneyInstrumentsCoordinator]


async def async_setup(hass: HomeAssistant, hass_config: dict) -> bool:
    """Set up the Honey Instruments integration."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(
    hass: HomeAssistant, entry: HoneyInstrumentsConfigEntry
) -> bool:
    """Set up Honey Instruments from a config entry."""
    session = async_get_clientsession(hass)
    api = HoneyInstrumentsApi(
        session=session,
        email=entry.data[CONF_EMAIL],
        password=entry.data[CONF_PASSWORD],
        access_token=entry.data.get(CONF_ACCESS_TOKEN),
    )

    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    coordinator = HoneyInstrumentsCoordinator(hass, api, scan_interval=scan_interval)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    hass.data[DOMAIN][entry.entry_id] = coordinator

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: HoneyInstrumentsConfigEntry
) -> bool:
    """Handle removal of an entry."""
    if unloaded := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unloaded


async def async_reload_entry(
    hass: HomeAssistant, entry: HoneyInstrumentsConfigEntry
) -> None:
    """Reload config entry when options change."""
    LOGGER.debug("Reloading config entry %s", entry.entry_id)
    await hass.config_entries.async_reload(entry.entry_id)
