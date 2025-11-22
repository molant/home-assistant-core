"""Support for Abode Security System binary sensors."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from jaraco.abode.devices.binary_sensor import BinarySensor

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util.enum import try_parse_enum

from .entity import AbodeDevice

if TYPE_CHECKING:
    from . import AbodeConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AbodeConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Abode binary sensor devices."""
    device_types = [
        "connectivity",
        "moisture",
        "motion",
        "occupancy",
        "door",
    ]

    async_add_entities(
        AbodeBinarySensor(entry, device)
        for device in entry.runtime_data.abode.get_devices(generic_type=device_types)
    )


class AbodeBinarySensor(AbodeDevice, BinarySensorEntity):
    """A binary sensor implementation for Abode device."""

    _attr_name = None
    _device: BinarySensor

    @property
    def is_on(self) -> bool:
        """Return True if the binary sensor is on."""
        return cast(bool, self._device.is_on)

    @property
    def device_class(self) -> BinarySensorDeviceClass | None:
        """Return the class of the binary sensor."""
        if self._device.get_value("is_window") == "1":
            return BinarySensorDeviceClass.WINDOW
        return try_parse_enum(BinarySensorDeviceClass, self._device.generic_type)
