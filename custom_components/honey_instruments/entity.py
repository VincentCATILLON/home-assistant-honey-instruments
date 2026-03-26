from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, VERSION_MAP
from .coordinator import HoneyInstrumentsCoordinator


class HoneyInstrumentsEntity(CoordinatorEntity[HoneyInstrumentsCoordinator]):
    """Base class for Honey Instruments entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: HoneyInstrumentsCoordinator,
        device_id: int,
        device_info_raw: dict[str, Any],
    ) -> None:
        super().__init__(coordinator)
        self._device_id = device_id

        device_name = device_info_raw.get("name", f"Balance {device_id}")
        version_code = device_info_raw.get("version", -1)
        conn_type = VERSION_MAP.get(version_code, "Unknown")

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, str(device_id))},
            name=device_name,
            manufacturer=MANUFACTURER,
            model=f"Balance ({conn_type})",
        )
