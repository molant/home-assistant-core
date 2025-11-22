"""Support for Abode Security System covers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from jaraco.abode.devices.cover import Cover

from homeassistant.components.cover import CoverEntity
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
    """Set up Abode cover devices."""
    async_add_entities(
        AbodeCover(entry, device)
        for device in entry.runtime_data.abode.get_devices(generic_type="cover")
    )


class AbodeCover(AbodeDevice, CoverEntity):
    """Representation of an Abode cover."""

    _device: Cover
    _attr_name = None

    @property
    def is_closed(self) -> bool:
        """Return true if cover is closed, else False."""
        return not self._device.is_open

    def close_cover(self, **kwargs: Any) -> None:
        """Issue close command to cover."""
        self._device.close_cover()

    def open_cover(self, **kwargs: Any) -> None:
        """Issue open command to cover."""
        self._device.open_cover()
