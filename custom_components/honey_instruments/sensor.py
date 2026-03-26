"""Sensor platform for Honey Instruments."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS,
    UnitOfElectricPotential,
    UnitOfMass,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import HoneyInstrumentsConfigEntry
from .coordinator import HoneyInstrumentsCoordinator
from .entity import HoneyInstrumentsEntity


@dataclass(frozen=True, kw_only=True)
class HoneyInstrumentsSensorDescription(SensorEntityDescription):
    """Describe a Honey Instruments sensor."""

    value_fn: Callable[[dict[str, Any]], Any]


SENSOR_DESCRIPTIONS: tuple[HoneyInstrumentsSensorDescription, ...] = (
    HoneyInstrumentsSensorDescription(
        key="weight",
        translation_key="weight",
        native_unit_of_measurement=UnitOfMass.KILOGRAMS,
        device_class=SensorDeviceClass.WEIGHT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("weight"),
    ),
    HoneyInstrumentsSensorDescription(
        key="weight_variation_1h",
        translation_key="weight_variation_1h",
        native_unit_of_measurement=UnitOfMass.KILOGRAMS,
        device_class=SensorDeviceClass.WEIGHT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("weightVar1h"),
    ),
    HoneyInstrumentsSensorDescription(
        key="weight_variation_24h",
        translation_key="weight_variation_24h",
        native_unit_of_measurement=UnitOfMass.KILOGRAMS,
        device_class=SensorDeviceClass.WEIGHT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("weightVar24h"),
    ),
    HoneyInstrumentsSensorDescription(
        key="weight_variation_7d",
        translation_key="weight_variation_7d",
        native_unit_of_measurement=UnitOfMass.KILOGRAMS,
        device_class=SensorDeviceClass.WEIGHT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("weightVar7j"),
    ),
    HoneyInstrumentsSensorDescription(
        key="temperature",
        translation_key="temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("temperature"),
    ),
    HoneyInstrumentsSensorDescription(
        key="battery_voltage",
        translation_key="battery_voltage",
        native_unit_of_measurement=UnitOfElectricPotential.MILLIVOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("batVoltage"),
    ),
    HoneyInstrumentsSensorDescription(
        key="signal_strength",
        translation_key="signal_strength",
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("signal"),
    ),
    HoneyInstrumentsSensorDescription(
        key="external_temperature",
        translation_key="external_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: (d.get("sensor") or {}).get("temperature"),
    ),
    HoneyInstrumentsSensorDescription(
        key="external_humidity",
        translation_key="external_humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: (d.get("sensor") or {}).get("hygrometry"),
    ),
    HoneyInstrumentsSensorDescription(
        key="external_battery_voltage",
        translation_key="external_battery_voltage",
        native_unit_of_measurement=UnitOfElectricPotential.MILLIVOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: (d.get("sensor") or {}).get("batVoltage"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HoneyInstrumentsConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Honey Instruments sensors from a config entry."""
    coordinator = entry.runtime_data

    entities: list[HoneyInstrumentsSensor] = []
    for device_id, device_data in coordinator.data.items():
        for description in SENSOR_DESCRIPTIONS:
            entities.append(
                HoneyInstrumentsSensor(
                    coordinator=coordinator,
                    description=description,
                    device_id=device_id,
                    device_info_raw=device_data["device"],
                )
            )

    async_add_entities(entities)


class HoneyInstrumentsSensor(HoneyInstrumentsEntity, SensorEntity):
    """Representation of a Honey Instruments sensor."""

    entity_description: HoneyInstrumentsSensorDescription

    def __init__(
        self,
        coordinator: HoneyInstrumentsCoordinator,
        description: HoneyInstrumentsSensorDescription,
        device_id: int,
        device_info_raw: dict[str, Any],
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, device_id, device_info_raw)
        self.entity_description = description
        self._attr_unique_id = f"{device_id}_{description.key}"

    @property
    def native_value(self) -> float | None:
        """Return the sensor value from the coordinator data."""
        device_entry = self.coordinator.data.get(self._device_id)
        if not device_entry:
            return None
        return self.entity_description.value_fn(device_entry.get("data", {}))
