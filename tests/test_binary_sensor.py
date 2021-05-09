"""The test for the snowtire binary sensor platform."""
# pylint: disable=redefined-outer-name
from unittest.mock import MagicMock

import pytest
from homeassistant.components.weather import (
    ATTR_FORECAST,
    ATTR_FORECAST_TEMP,
    ATTR_FORECAST_TEMP_LOW,
    ATTR_FORECAST_TIME,
    ATTR_WEATHER_TEMPERATURE,
)
from homeassistant.const import CONF_PLATFORM, TEMP_CELSIUS, TEMP_FAHRENHEIT
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.util import dt as dt_util
from pytest import raises

from custom_components.snowtire.binary_sensor import (
    SnowtireBinarySensor,
    async_setup_platform,
)
from custom_components.snowtire.const import (
    CONF_WEATHER,
    DOMAIN,
    ICON_SUMMER,
    ICON_WINTER,
)

MOCK_UNIQUE_ID = "test_id"
MOCK_NAME = "test_name"
MOCK_WEATHER_ENTITY = "weather.test"
MOCK_DAYS = 1

MOCK_CONFIG = {
    CONF_PLATFORM: DOMAIN,
    CONF_WEATHER: MOCK_WEATHER_ENTITY,
}


@pytest.fixture()
def default_sensor(hass: HomeAssistant):
    """Create an AverageSensor with default values."""
    entity = SnowtireBinarySensor(
        MOCK_UNIQUE_ID, MOCK_NAME, MOCK_WEATHER_ENTITY, MOCK_DAYS
    )
    entity.hass = hass
    return entity


async def test_setup_platform(hass: HomeAssistant):
    """Test platform setup."""
    async_add_entities = MagicMock()

    await async_setup_platform(hass, MOCK_CONFIG, async_add_entities, None)
    assert async_add_entities.called


async def test_sensor_initialization(default_sensor):
    """Test sensor initialization."""
    assert default_sensor.unique_id == MOCK_UNIQUE_ID
    assert default_sensor.device_class == f"{DOMAIN}__type"
    assert default_sensor.name == MOCK_NAME
    assert default_sensor.should_poll is False
    assert default_sensor.is_on is None
    assert default_sensor.icon == ICON_WINTER
    assert default_sensor.available is False

    entity = SnowtireBinarySensor(None, MOCK_NAME, MOCK_WEATHER_ENTITY, MOCK_DAYS)
    assert entity.unique_id is None

    entity = SnowtireBinarySensor(
        "__legacy__", MOCK_NAME, MOCK_WEATHER_ENTITY, MOCK_DAYS
    )
    assert entity.unique_id == f"{MOCK_WEATHER_ENTITY}-1"


async def test_async_added_to_hass(default_sensor):
    """Test async added to hass."""
    await default_sensor.async_added_to_hass()


# pylint: disable=protected-access
async def test__temp2c():
    """Test temperature conversions."""
    assert SnowtireBinarySensor._temp2c(10, TEMP_CELSIUS) == 10
    assert round(SnowtireBinarySensor._temp2c(10, TEMP_FAHRENHEIT), 2) == -12.22
    assert SnowtireBinarySensor._temp2c(None, TEMP_CELSIUS) is None


async def test_async_update(hass: HomeAssistant, default_sensor):
    """Test sensor update."""
    hass.states._states[MOCK_WEATHER_ENTITY] = None

    with raises(HomeAssistantError):
        await default_sensor.async_update()

    hass.states.async_set(MOCK_WEATHER_ENTITY, "State")

    with raises(HomeAssistantError):
        await default_sensor.async_update()

    today = dt_util.start_of_local_day()
    today_ts = int(today.timestamp() * 1000)
    day = days = 86400000

    forecast = [
        {
            ATTR_FORECAST_TIME: today_ts - day,
        },
        {
            ATTR_FORECAST_TIME: today,
            ATTR_FORECAST_TEMP: 9,
        },
        {
            ATTR_FORECAST_TIME: today_ts + day,
            ATTR_FORECAST_TEMP_LOW: 1,
            ATTR_FORECAST_TEMP: 8,
        },
        {
            ATTR_FORECAST_TIME: today_ts + (MOCK_DAYS + 1) * days,
        },
    ]

    hass.states.async_set(
        MOCK_WEATHER_ENTITY,
        "State",
        attributes={
            ATTR_WEATHER_TEMPERATURE: -1,
            ATTR_FORECAST: forecast,
        },
    )

    await default_sensor.async_update()
    assert default_sensor.available
    assert default_sensor.is_on
    assert default_sensor.icon == ICON_WINTER

    hass.states.async_set(
        MOCK_WEATHER_ENTITY,
        "State",
        attributes={
            ATTR_WEATHER_TEMPERATURE: 9.9,
            ATTR_FORECAST: forecast,
        },
    )

    await default_sensor.async_update()
    assert default_sensor.available
    assert default_sensor.is_on
    assert default_sensor.icon == ICON_WINTER

    hass.states.async_set(
        MOCK_WEATHER_ENTITY,
        "State",
        attributes={
            ATTR_WEATHER_TEMPERATURE: 10,
            ATTR_FORECAST: forecast,
        },
    )

    await default_sensor.async_update()
    assert default_sensor.available
    assert default_sensor.is_on is False
    assert default_sensor.icon == ICON_SUMMER
