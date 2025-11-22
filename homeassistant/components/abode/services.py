"""Support for the Abode Security System."""

from __future__ import annotations

from typing import TYPE_CHECKING

from jaraco.abode.exceptions import Exception as AbodeException
import voluptuous as vol

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.dispatcher import dispatcher_send

from .const import DOMAIN, LOGGER

if TYPE_CHECKING:
    from . import AbodeConfigEntry

SERVICE_SETTINGS = "change_setting"
SERVICE_CAPTURE_IMAGE = "capture_image"
SERVICE_TRIGGER_AUTOMATION = "trigger_automation"
SERVICE_TRIGGER_ALARM = "trigger_alarm"
SERVICE_ACKNOWLEDGE_ALARM = "acknowledge_alarm"
SERVICE_DISMISS_ALARM = "dismiss_alarm"
SERVICE_ENABLE_TEST_MODE = "enable_test_mode"
SERVICE_DISABLE_TEST_MODE = "disable_test_mode"

ATTR_SETTING = "setting"
ATTR_VALUE = "value"
ATTR_ALARM_TYPE = "alarm_type"
ATTR_TIMELINE_ID = "timeline_id"


CHANGE_SETTING_SCHEMA = vol.Schema(
    {vol.Required(ATTR_SETTING): cv.string, vol.Required(ATTR_VALUE): cv.string}
)

CAPTURE_IMAGE_SCHEMA = vol.Schema({ATTR_ENTITY_ID: cv.entity_ids})

AUTOMATION_SCHEMA = vol.Schema({ATTR_ENTITY_ID: cv.entity_ids})

TRIGGER_ALARM_SCHEMA = vol.Schema({vol.Required(ATTR_ALARM_TYPE): cv.string})

ACKNOWLEDGE_ALARM_SCHEMA = vol.Schema({vol.Required(ATTR_TIMELINE_ID): cv.string})

DISMISS_ALARM_SCHEMA = vol.Schema({vol.Required(ATTR_TIMELINE_ID): cv.string})

ENABLE_TEST_MODE_SCHEMA = vol.Schema({})

DISABLE_TEST_MODE_SCHEMA = vol.Schema({})


def _get_abode_entry(hass: HomeAssistant) -> AbodeConfigEntry:
    """Get the first loaded Abode config entry."""
    for entry in hass.config_entries.async_entries(DOMAIN):
        if entry.state is ConfigEntryState.LOADED:
            return entry  # type: ignore[return-value]
    raise ServiceValidationError("No Abode integration loaded")


def _change_setting(call: ServiceCall) -> None:
    """Change an Abode system setting."""
    entry = _get_abode_entry(call.hass)
    setting = call.data[ATTR_SETTING]
    value = call.data[ATTR_VALUE]

    try:
        entry.runtime_data.abode.set_setting(setting, value)
    except AbodeException as ex:
        LOGGER.warning(ex)


def _capture_image(call: ServiceCall) -> None:
    """Capture a new image."""
    entity_ids = call.data[ATTR_ENTITY_ID]

    target_entities = [
        entity_id
        for entity_id in call.hass.data[DOMAIN]["entity_ids"]
        if entity_id in entity_ids
    ]

    for entity_id in target_entities:
        signal = f"abode_camera_capture_{entity_id}"
        dispatcher_send(call.hass, signal)


def _trigger_automation(call: ServiceCall) -> None:
    """Trigger an Abode automation."""
    entity_ids = call.data[ATTR_ENTITY_ID]

    target_entities = [
        entity_id
        for entity_id in call.hass.data[DOMAIN]["entity_ids"]
        if entity_id in entity_ids
    ]

    for entity_id in target_entities:
        signal = f"abode_trigger_automation_{entity_id}"
        dispatcher_send(call.hass, signal)


async def _trigger_alarm(call: ServiceCall) -> None:
    """Trigger a manual alarm."""
    entry = _get_abode_entry(call.hass)
    alarm_type = call.data[ATTR_ALARM_TYPE]

    try:
        alarm = await call.hass.async_add_executor_job(
            entry.runtime_data.abode.get_alarm
        )
        await call.hass.async_add_executor_job(
            alarm.trigger_manual_alarm, alarm_type
        )
        LOGGER.info("Triggered manual alarm of type: %s", alarm_type)
    except AbodeException as ex:
        LOGGER.error("Failed to trigger manual alarm: %s", ex)


async def _acknowledge_alarm(call: ServiceCall) -> None:
    """Acknowledge a timeline alarm event."""
    entry = _get_abode_entry(call.hass)
    timeline_id = call.data[ATTR_TIMELINE_ID]

    try:
        await call.hass.async_add_executor_job(
            entry.runtime_data.abode.acknowledge_timeline_event, timeline_id
        )
        LOGGER.info("Acknowledged timeline event: %s", timeline_id)
    except AbodeException as ex:
        LOGGER.error("Failed to acknowledge timeline event: %s", ex)


async def _dismiss_alarm(call: ServiceCall) -> None:
    """Dismiss a timeline alarm event."""
    entry = _get_abode_entry(call.hass)
    timeline_id = call.data[ATTR_TIMELINE_ID]

    try:
        await call.hass.async_add_executor_job(
            entry.runtime_data.abode.dismiss_timeline_event, timeline_id
        )
        LOGGER.info("Dismissed timeline event: %s", timeline_id)
    except AbodeException as ex:
        LOGGER.error("Failed to dismiss timeline event: %s", ex)


async def _enable_test_mode(call: ServiceCall) -> None:
    """Enable test mode."""
    entry = _get_abode_entry(call.hass)
    try:
        await call.hass.async_add_executor_job(
            entry.runtime_data.abode.set_test_mode, True
        )
        LOGGER.info("Test mode enabled")
    except AbodeException as ex:
        LOGGER.error("Failed to enable test mode: %s", ex)


async def _disable_test_mode(call: ServiceCall) -> None:
    """Disable test mode."""
    entry = _get_abode_entry(call.hass)
    try:
        await call.hass.async_add_executor_job(
            entry.runtime_data.abode.set_test_mode, False
        )
        LOGGER.info("Test mode disabled")
    except AbodeException as ex:
        LOGGER.error("Failed to disable test mode: %s", ex)


@callback
def async_setup_services(hass: HomeAssistant) -> None:
    """Home Assistant services."""

    hass.services.async_register(
        DOMAIN, SERVICE_SETTINGS, _change_setting, schema=CHANGE_SETTING_SCHEMA
    )

    hass.services.async_register(
        DOMAIN, SERVICE_CAPTURE_IMAGE, _capture_image, schema=CAPTURE_IMAGE_SCHEMA
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_TRIGGER_AUTOMATION,
        _trigger_automation,
        schema=AUTOMATION_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN, SERVICE_TRIGGER_ALARM, _trigger_alarm, schema=TRIGGER_ALARM_SCHEMA
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_ACKNOWLEDGE_ALARM,
        _acknowledge_alarm,
        schema=ACKNOWLEDGE_ALARM_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN, SERVICE_DISMISS_ALARM, _dismiss_alarm, schema=DISMISS_ALARM_SCHEMA
    )

    hass.services.async_register(
        DOMAIN, SERVICE_ENABLE_TEST_MODE, _enable_test_mode, schema=ENABLE_TEST_MODE_SCHEMA
    )

    hass.services.async_register(
        DOMAIN, SERVICE_DISABLE_TEST_MODE, _disable_test_mode, schema=DISABLE_TEST_MODE_SCHEMA
    )
