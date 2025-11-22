"""Support for Abode Security System alarm control panels."""

from __future__ import annotations

from typing import TYPE_CHECKING

from jaraco.abode.devices.alarm import Alarm
from jaraco.abode.exceptions import Exception as AbodeException

from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    AlarmControlPanelEntityFeature,
    AlarmControlPanelState,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import LOGGER
from .entity import AbodeDevice

if TYPE_CHECKING:
    from . import AbodeConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AbodeConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Abode alarm control panel device."""
    async_add_entities(
        [
            AbodeAlarm(
                entry, await hass.async_add_executor_job(entry.runtime_data.abode.get_alarm)
            )
        ]
    )


class AbodeAlarm(AbodeDevice, AlarmControlPanelEntity):
    """An alarm_control_panel implementation for Abode."""

    _attr_name = None
    _attr_code_arm_required = False
    _attr_supported_features = (
        AlarmControlPanelEntityFeature.ARM_HOME
        | AlarmControlPanelEntityFeature.ARM_AWAY
    )
    _device: Alarm

    @property
    def alarm_state(self) -> AlarmControlPanelState | None:
        """Return the state of the device."""
        if self._device.is_standby:
            return AlarmControlPanelState.DISARMED
        if self._device.is_away:
            return AlarmControlPanelState.ARMED_AWAY
        if self._device.is_home:
            return AlarmControlPanelState.ARMED_HOME
        return None

    def alarm_disarm(self, code: str | None = None) -> None:
        """Send disarm command."""
        self._device.set_standby()

    def alarm_arm_home(self, code: str | None = None) -> None:
        """Send arm home command."""
        self._device.set_home()

    def alarm_arm_away(self, code: str | None = None) -> None:
        """Send arm away command."""
        self._device.set_away()

    def trigger_manual_alarm(self, alarm_type: str) -> None:
        """Trigger a manual alarm."""
        try:
            self._device.trigger_manual_alarm(alarm_type)
            LOGGER.info("Triggered manual alarm of type: %s", alarm_type)
        except AbodeException as ex:
            LOGGER.error("Failed to trigger manual alarm: %s", ex)

    def acknowledge_timeline_event(self, timeline_id: str) -> None:
        """Acknowledge a timeline alarm event."""
        try:
            self._data.abode.acknowledge_timeline_event(timeline_id)
            LOGGER.info("Acknowledged timeline event: %s", timeline_id)
        except AbodeException as ex:
            LOGGER.error("Failed to acknowledge timeline event: %s", ex)

    def dismiss_timeline_event(self, timeline_id: str) -> None:
        """Dismiss a timeline alarm event."""
        try:
            self._data.abode.dismiss_timeline_event(timeline_id)
            LOGGER.info("Dismissed timeline event: %s", timeline_id)
        except AbodeException as ex:
            LOGGER.error("Failed to dismiss timeline event: %s", ex)

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Return the state attributes."""
        return {
            "device_id": self._device.id,
            "battery_backup": self._device.battery,
            "cellular_backup": self._device.is_cellular,
        }
