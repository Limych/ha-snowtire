"""The test for the snowtire binary sensor platform."""

# pylint: disable=redefined-outer-name
from typing import Final
from unittest.mock import MagicMock, patch

import pytest
from homeassistant.components.weather import (
    ATTR_FORECAST_TEMP,
    ATTR_FORECAST_TEMP_LOW,
    ATTR_FORECAST_TIME,
    ATTR_WEATHER_TEMPERATURE,
    SERVICE_GET_FORECASTS,
    WeatherEntityFeature,
)
from homeassistant.components.weather import (
    DOMAIN as WEATHER_DOMAIN,
)
from homeassistant.const import (
    ATTR_SUPPORTED_FEATURES,
    CONF_NAME,
    CONF_PLATFORM,
    CONF_TYPE,
    CONF_UNIQUE_ID,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, ServiceRegistry, SupportsResponse
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.typing import ConfigType
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_mock_service

from custom_components.snowtire.binary_sensor import (
    SnowtireBinarySensor,
    async_setup_platform,
)
from custom_components.snowtire.const import (
    CONF_CREATE_NOTIFICATIONS,
    CONF_DAYS,
    CONF_WEATHER,
    DOMAIN,
    ICON_SUMMER,
    ICON_WINTER,
)

MOCK_UNIQUE_ID: Final = "test_id"
MOCK_NAME: Final = "test_name"
MOCK_WEATHER_ENTITY: Final = "weather.test"
MOCK_DAYS: Final = 1


@pytest.fixture(name="config")
def config_fixture(hass: HomeAssistant) -> ConfigType:
    """Return default config for tests."""
    return {
        CONF_UNIQUE_ID: MOCK_UNIQUE_ID,
        CONF_NAME: MOCK_NAME,
        CONF_WEATHER: MOCK_WEATHER_ENTITY,
        CONF_DAYS: MOCK_DAYS,
        CONF_CREATE_NOTIFICATIONS: True,
    }


@pytest.fixture(name="default_sensor")
def default_sensor_fixture(hass: HomeAssistant, config):
    """Create an AverageSensor with default values."""
    return SnowtireBinarySensor(hass, config)


async def test_setup_platform(hass: HomeAssistant, caplog):
    """Test platform setup."""
    async_add_entities = MagicMock()

    caplog.clear()
    config = {
        CONF_PLATFORM: DOMAIN,
        CONF_WEATHER: MOCK_WEATHER_ENTITY,
    }
    await async_setup_platform(hass, config, async_add_entities, None)

    assert async_add_entities.called
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "INFO"


async def test_sensor_initialization(hass: HomeAssistant, default_sensor, config):
    """Test sensor initialization."""
    assert default_sensor.unique_id == MOCK_UNIQUE_ID
    assert default_sensor.device_class is None
    assert default_sensor.should_poll is False
    assert default_sensor.is_on is None
    assert default_sensor.icon == ICON_WINTER
    assert default_sensor.available is False

    config[CONF_UNIQUE_ID] = None
    entity = SnowtireBinarySensor(hass, config)
    assert entity.unique_id is None

    config[CONF_UNIQUE_ID] = "__legacy__"
    entity = SnowtireBinarySensor(hass, config)
    assert entity.unique_id == f"{MOCK_WEATHER_ENTITY}-1"


async def test_async_added_to_hass(default_sensor):
    """Test async added to hass."""
    await default_sensor.async_added_to_hass()


# pylint: disable=protected-access
@pytest.mark.parametrize(
    ("temp1", "temp2"),
    [(0, -17.78), (10, -12.22), (20, -6.67), (30, -1.11), (40, 4.44), (50, 10)],
)
async def test__temp2c(temp1, temp2):
    """Test temperature conversions."""
    assert SnowtireBinarySensor._temp2c(temp1, UnitOfTemperature.CELSIUS) == temp1
    assert (
        round(SnowtireBinarySensor._temp2c(temp1, UnitOfTemperature.FAHRENHEIT), 2)
        == temp2
    )
    assert SnowtireBinarySensor._temp2c(None, UnitOfTemperature.CELSIUS) is None


async def test_async_update_forecast_fail(hass: HomeAssistant, default_sensor):
    """Test sensor update on forecast fail."""
    async_mock_service(
        hass,
        WEATHER_DOMAIN,
        SERVICE_GET_FORECASTS,
        supports_response=SupportsResponse.OPTIONAL,
    )

    with pytest.raises(HomeAssistantError, match="Unable to find an entity"):
        await default_sensor.async_update()

    hass.states.async_set(
        MOCK_WEATHER_ENTITY,
        "State",
        attributes={
            ATTR_WEATHER_TEMPERATURE: -1,
        },
    )

    with pytest.raises(HomeAssistantError, match="doesn't support any forecast"):
        await default_sensor.async_update()

    hass.states.async_set(
        MOCK_WEATHER_ENTITY,
        "State",
        attributes={
            ATTR_WEATHER_TEMPERATURE: -1,
            ATTR_SUPPORTED_FEATURES: "unexpected",
        },
    )

    with pytest.raises(TypeError):
        await default_sensor.async_update()


async def test_async_update(hass: HomeAssistant, default_sensor):
    """Test sensor update."""
    hass.states.async_set(MOCK_WEATHER_ENTITY, None)

    with pytest.raises(HomeAssistantError):
        await default_sensor.async_update()

    hass.states.async_set(MOCK_WEATHER_ENTITY, "State")

    with pytest.raises(HomeAssistantError):
        await default_sensor.async_update()

    hass.states.async_set(
        MOCK_WEATHER_ENTITY,
        "State",
        attributes={
            ATTR_WEATHER_TEMPERATURE: -1,
            ATTR_SUPPORTED_FEATURES: WeatherEntityFeature.FORECAST_DAILY
            | WeatherEntityFeature.FORECAST_TWICE_DAILY
            | WeatherEntityFeature.FORECAST_HOURLY,
        },
    )

    with patch.object(ServiceRegistry, "async_call") as call:
        await default_sensor.async_update()
        assert call.call_args.args[2][CONF_TYPE] == "daily"

    hass.states.async_set(
        MOCK_WEATHER_ENTITY,
        "State",
        attributes={
            ATTR_WEATHER_TEMPERATURE: -1,
            ATTR_SUPPORTED_FEATURES: WeatherEntityFeature.FORECAST_TWICE_DAILY
            | WeatherEntityFeature.FORECAST_HOURLY,
        },
    )

    with patch.object(ServiceRegistry, "async_call") as call:
        await default_sensor.async_update()
        assert call.call_args.args[2][CONF_TYPE] == "twice_daily"

    hass.states.async_set(
        MOCK_WEATHER_ENTITY,
        "State",
        attributes={
            ATTR_WEATHER_TEMPERATURE: -1,
            ATTR_SUPPORTED_FEATURES: WeatherEntityFeature.FORECAST_HOURLY,
        },
    )

    with patch.object(ServiceRegistry, "async_call") as call:
        await default_sensor.async_update()
        assert call.call_args.args[2][CONF_TYPE] == "hourly"

    today = dt_util.start_of_local_day()
    today_ts = int(today.timestamp() * 1000)
    day = days = 86400000

    forecast = {
        MOCK_WEATHER_ENTITY: {
            "forecast": [
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
        }
    }

    async_mock_service(hass, WEATHER_DOMAIN, SERVICE_GET_FORECASTS, response=forecast)

    hass.states.async_set(
        MOCK_WEATHER_ENTITY,
        "State",
        attributes={
            ATTR_WEATHER_TEMPERATURE: -1,
            ATTR_SUPPORTED_FEATURES: WeatherEntityFeature.FORECAST_DAILY,
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
            ATTR_WEATHER_TEMPERATURE: 11.9,
            ATTR_SUPPORTED_FEATURES: WeatherEntityFeature.FORECAST_DAILY,
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
            ATTR_WEATHER_TEMPERATURE: 12,
            ATTR_SUPPORTED_FEATURES: WeatherEntityFeature.FORECAST_DAILY,
        },
    )

    await default_sensor.async_update()
    assert default_sensor.available
    assert not default_sensor.is_on
    assert default_sensor.icon == ICON_SUMMER

    hass.states.async_set(
        MOCK_WEATHER_ENTITY,
        "State",
        attributes={
            ATTR_WEATHER_TEMPERATURE: 8,
            ATTR_SUPPORTED_FEATURES: WeatherEntityFeature.FORECAST_DAILY,
        },
    )

    await default_sensor.async_update()
    assert default_sensor.available
    assert not default_sensor.is_on
    assert default_sensor.icon == ICON_SUMMER

    hass.states.async_set(
        MOCK_WEATHER_ENTITY,
        "State",
        attributes={
            ATTR_WEATHER_TEMPERATURE: 7.9,
            ATTR_SUPPORTED_FEATURES: WeatherEntityFeature.FORECAST_DAILY,
        },
    )

    await default_sensor.async_update()
    assert default_sensor.available
    assert default_sensor.is_on
    assert default_sensor.icon == ICON_WINTER
