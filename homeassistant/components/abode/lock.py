"""Support for the Abode Security System locks."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from jaraco.abode.devices.lock import Lock

from homeassistant.components.lock import LockEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .entity import AbodeDevice

if TYPE_CHECKING:
    from . import AbodeConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AbodeConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Abode lock devices."""
    async_add_entities(
        AbodeLock(entry, device)
        for device in entry.runtime_data.abode.get_devices(generic_type="lock")
    )


class AbodeLock(AbodeDevice, LockEntity):
    """Representation of an Abode lock."""

    _device: Lock
    _attr_name = None

    def lock(self, **kwargs: Any) -> None:
        """Lock the device."""
        self._device.lock()

    def unlock(self, **kwargs: Any) -> None:
        """Unlock the device."""
        self._device.unlock()

    @property
    def is_locked(self) -> bool:
        """Return true if device is on."""
        return bool(self._device.is_locked)
