"""Tests for the Abode switch device."""

from unittest.mock import patch

from homeassistant.components.abode.const import DOMAIN
from homeassistant.components.abode.services import (
    SERVICE_ACKNOWLEDGE_ALARM,
    SERVICE_DISMISS_ALARM,
    SERVICE_TRIGGER_ALARM,
    SERVICE_TRIGGER_AUTOMATION,
)
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.const import (
    ATTR_ENTITY_ID,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    STATE_OFF,
    STATE_ON,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .common import setup_platform

AUTOMATION_ID = "switch.test_automation"
AUTOMATION_UID = "47fae27488f74f55b964a81a066c3a01"
DEVICE_ID = "switch.test_switch"
DEVICE_UID = "0012a4d3614cb7e2b8c9abea31d2fb2a"
PANIC_ALARM_ID = "switch.test_alarm_panic_alarm"
TEST_MODE_ID = "switch.test_alarm_test_mode"


async def test_entity_registry(
    hass: HomeAssistant, entity_registry: er.EntityRegistry
) -> None:
    """Tests that the devices are registered in the entity registry."""
    await setup_platform(hass, SWITCH_DOMAIN)

    entry = entity_registry.async_get(AUTOMATION_ID)
    assert entry.unique_id == AUTOMATION_UID

    entry = entity_registry.async_get(DEVICE_ID)
    assert entry.unique_id == DEVICE_UID


async def test_attributes(hass: HomeAssistant) -> None:
    """Test the switch attributes are correct."""
    await setup_platform(hass, SWITCH_DOMAIN)

    state = hass.states.get(DEVICE_ID)
    assert state.state == STATE_OFF


async def test_switch_on(hass: HomeAssistant) -> None:
    """Test the switch can be turned on."""
    await setup_platform(hass, SWITCH_DOMAIN)

    with patch("jaraco.abode.devices.switch.Switch.switch_on") as mock_switch_on:
        await hass.services.async_call(
            SWITCH_DOMAIN, SERVICE_TURN_ON, {ATTR_ENTITY_ID: DEVICE_ID}, blocking=True
        )
        await hass.async_block_till_done()

        mock_switch_on.assert_called_once()


async def test_switch_off(hass: HomeAssistant) -> None:
    """Test the switch can be turned off."""
    await setup_platform(hass, SWITCH_DOMAIN)

    with patch("jaraco.abode.devices.switch.Switch.switch_off") as mock_switch_off:
        await hass.services.async_call(
            SWITCH_DOMAIN, SERVICE_TURN_OFF, {ATTR_ENTITY_ID: DEVICE_ID}, blocking=True
        )
        await hass.async_block_till_done()

        mock_switch_off.assert_called_once()


async def test_automation_attributes(hass: HomeAssistant) -> None:
    """Test the automation attributes are correct."""
    await setup_platform(hass, SWITCH_DOMAIN)

    state = hass.states.get(AUTOMATION_ID)
    # State is set based on "enabled" key in automation JSON.
    assert state.state == STATE_ON


async def test_turn_automation_off(hass: HomeAssistant) -> None:
    """Test the automation can be turned off."""
    with patch("jaraco.abode.automation.Automation.enable") as mock_trigger:
        await setup_platform(hass, SWITCH_DOMAIN)

        await hass.services.async_call(
            SWITCH_DOMAIN,
            SERVICE_TURN_OFF,
            {ATTR_ENTITY_ID: AUTOMATION_ID},
            blocking=True,
        )
        await hass.async_block_till_done()

        mock_trigger.assert_called_once_with(False)


async def test_turn_automation_on(hass: HomeAssistant) -> None:
    """Test the automation can be turned on."""
    with patch("jaraco.abode.automation.Automation.enable") as mock_trigger:
        await setup_platform(hass, SWITCH_DOMAIN)

        await hass.services.async_call(
            SWITCH_DOMAIN,
            SERVICE_TURN_ON,
            {ATTR_ENTITY_ID: AUTOMATION_ID},
            blocking=True,
        )
        await hass.async_block_till_done()

        mock_trigger.assert_called_once_with(True)


async def test_trigger_automation(hass: HomeAssistant) -> None:
    """Test the trigger automation service."""
    await setup_platform(hass, SWITCH_DOMAIN)

    with patch("jaraco.abode.automation.Automation.trigger") as mock:
        await hass.services.async_call(
            DOMAIN,
            SERVICE_TRIGGER_AUTOMATION,
            {ATTR_ENTITY_ID: AUTOMATION_ID},
            blocking=True,
        )
        await hass.async_block_till_done()

        mock.assert_called_once()


async def test_manual_alarm_switch_attributes(hass: HomeAssistant) -> None:
    """Test the manual alarm switch attributes are correct."""
    await setup_platform(hass, SWITCH_DOMAIN)

    state = hass.states.get(PANIC_ALARM_ID)
    assert state is not None
    assert state.state == STATE_OFF


async def test_manual_alarm_switch_turn_on(hass: HomeAssistant) -> None:
    """Test the manual alarm switch can be turned on."""
    await setup_platform(hass, SWITCH_DOMAIN)

    with patch("jaraco.abode.devices.alarm.Alarm.trigger_manual_alarm") as mock:
        mock.return_value = {"event_id": "test_event_123"}
        await hass.services.async_call(
            SWITCH_DOMAIN,
            SERVICE_TURN_ON,
            {ATTR_ENTITY_ID: PANIC_ALARM_ID},
            blocking=True,
        )
        await hass.async_block_till_done()

        mock.assert_called_once_with("PANIC")


async def test_test_mode_switch_attributes(hass: HomeAssistant) -> None:
    """Test the test mode switch attributes are correct."""
    await setup_platform(hass, SWITCH_DOMAIN)

    state = hass.states.get(TEST_MODE_ID)
    assert state is not None


async def test_test_mode_switch_turn_on(hass: HomeAssistant) -> None:
    """Test the test mode switch can be turned on."""
    await setup_platform(hass, SWITCH_DOMAIN)

    with patch("jaraco.abode.Abode.set_test_mode") as mock:
        await hass.services.async_call(
            SWITCH_DOMAIN,
            SERVICE_TURN_ON,
            {ATTR_ENTITY_ID: TEST_MODE_ID},
            blocking=True,
        )
        await hass.async_block_till_done()

        mock.assert_called_once_with(True)


async def test_test_mode_switch_turn_off(hass: HomeAssistant) -> None:
    """Test the test mode switch can be turned off."""
    await setup_platform(hass, SWITCH_DOMAIN)

    with patch("jaraco.abode.Abode.set_test_mode") as mock:
        await hass.services.async_call(
            SWITCH_DOMAIN,
            SERVICE_TURN_OFF,
            {ATTR_ENTITY_ID: TEST_MODE_ID},
            blocking=True,
        )
        await hass.async_block_till_done()

        mock.assert_called_once_with(False)


async def test_trigger_alarm_service(hass: HomeAssistant) -> None:
    """Test the trigger alarm service."""
    await setup_platform(hass, SWITCH_DOMAIN)

    with patch("jaraco.abode.devices.alarm.Alarm.trigger_manual_alarm") as mock:
        await hass.services.async_call(
            DOMAIN,
            SERVICE_TRIGGER_ALARM,
            {"alarm_type": "PANIC"},
            blocking=True,
        )
        await hass.async_block_till_done()

        mock.assert_called_once_with("PANIC")


async def test_acknowledge_alarm_service(hass: HomeAssistant) -> None:
    """Test the acknowledge alarm service."""
    await setup_platform(hass, SWITCH_DOMAIN)

    with patch("jaraco.abode.Abode.acknowledge_timeline_event") as mock:
        await hass.services.async_call(
            DOMAIN,
            SERVICE_ACKNOWLEDGE_ALARM,
            {"timeline_id": "12345"},
            blocking=True,
        )
        await hass.async_block_till_done()

        mock.assert_called_once_with("12345")


async def test_dismiss_alarm_service(hass: HomeAssistant) -> None:
    """Test the dismiss alarm service."""
    await setup_platform(hass, SWITCH_DOMAIN)

    with patch("jaraco.abode.Abode.dismiss_timeline_event") as mock:
        await hass.services.async_call(
            DOMAIN,
            SERVICE_DISMISS_ALARM,
            {"timeline_id": "12345"},
            blocking=True,
        )
        await hass.async_block_till_done()

        mock.assert_called_once_with("12345")
