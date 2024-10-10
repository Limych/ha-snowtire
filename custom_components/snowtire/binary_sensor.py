#
#  Copyright (c) 2020-2021, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
#
"""
The Snowtire binary sensor.

For more details about this platform, please refer to the documentation at
https://github.com/Limych/ha-snowtire/
"""

import logging
from datetime import datetime
from typing import Final

import voluptuous as vol
from homeassistant.components.binary_sensor import BinarySensorEntity
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
    CONF_ENTITY_ID,
    CONF_NAME,
    CONF_TYPE,
    CONF_UNIQUE_ID,
    EVENT_HOMEASSISTANT_START,
    UnitOfTemperature,
)
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.util import dt as dt_util
from homeassistant.util.unit_conversion import TemperatureConverter

from .const import (
    CONF_DAYS,
    CONF_WEATHER,
    DEFAULT_DAYS,
    DEFAULT_NAME,
    DOMAIN,
    ICON_SUMMER,
    ICON_WINTER,
    STARTUP_MESSAGE,
)

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = cv.PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_WEATHER): cv.entity_domain(WEATHER_DOMAIN),
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_DAYS, default=DEFAULT_DAYS): cv.positive_int,
        vol.Optional(CONF_UNIQUE_ID): cv.string,
    }
)

TEMP_CHANGE: Final = 7
TEMP_ERROR: Final = 0.5


# pylint: disable=unused-argument
async def async_setup_platform(
    hass: HomeAssistant,  # noqa: ARG001
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType = None,  # noqa: ARG001
) -> None:
    """Set up the Snowtire sensor."""
    # Print startup message
    _LOGGER.info(STARTUP_MESSAGE)

    async_add_entities(
        [
            SnowtireBinarySensor(
                config.get(CONF_UNIQUE_ID),
                config.get(CONF_NAME),
                config.get(CONF_WEATHER),
                config.get(CONF_DAYS),
            )
        ]
    )


class SnowtireBinarySensor(BinarySensorEntity):
    """Implementation of an Snowtire binary sensor."""

    def __init__(
        self,
        unique_id: str | None,
        friendly_name: str,
        weather_entity: str,
        days: int,
    ) -> None:
        """Initialize the sensor."""
        self._weather_entity = weather_entity
        self._days = days

        self._attr_unique_id = (
            f"{self._weather_entity}-{self._days}"
            if unique_id == "__legacy__"
            else unique_id
        )
        self._attr_name = friendly_name
        self._attr_is_on = None
        self._attr_should_poll = False
        self._attr_device_class = f"{DOMAIN}__type"

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""

        @callback
        # pylint: disable=unused-argument
        def sensor_state_listener(event: Event) -> None:  # noqa: ARG001
            """Handle device state changes."""
            self.async_schedule_update_ha_state(force_refresh=True)

        @callback
        # pylint: disable=unused-argument
        def sensor_startup(event: Event) -> None:  # noqa: ARG001
            """Update template on startup."""
            async_track_state_change_event(
                self.hass, [self._weather_entity], sensor_state_listener
            )

            self.async_schedule_update_ha_state(force_refresh=True)

        self.hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, sensor_startup)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._attr_is_on is not None

    @property
    def icon(self) -> str | None:
        """Return the icon to use in the frontend, if any."""
        return ICON_SUMMER if self.is_on is False else ICON_WINTER

    @staticmethod
    def _temp2c(
        temperature: float | None, temperature_unit: str | None
    ) -> float | None:
        """Convert weather temperature to Celsius degree."""
        if temperature is not None and temperature_unit != UnitOfTemperature.CELSIUS:
            temperature = TemperatureConverter.convert(
                temperature, temperature_unit, UnitOfTemperature.CELSIUS
            )

        return temperature

    async def async_update(self) -> None:  # noqa: PLR0912
        """Update the sensor state."""
        wstate = self.hass.states.get(self._weather_entity)
        if wstate is None:
            msg = f"Unable to find an entity called {self._weather_entity}"
            raise HomeAssistantError(msg)

        tmpu = self.hass.config.units.temperature_unit
        temp = wstate.attributes.get(ATTR_WEATHER_TEMPERATURE)

        wfeatures = wstate.attributes.get(ATTR_SUPPORTED_FEATURES) or 0
        if (wfeatures & WeatherEntityFeature.FORECAST_DAILY) != 0:
            forecast_type = "daily"
        elif (wfeatures & WeatherEntityFeature.FORECAST_TWICE_DAILY) != 0:
            forecast_type = "twice_daily"
        elif (wfeatures & WeatherEntityFeature.FORECAST_HOURLY) != 0:
            forecast_type = "hourly"
        else:
            msg = "Weather entity doesn't support any forecast"
            raise HomeAssistantError(msg)

        try:
            forecast = await self.hass.services.async_call(
                WEATHER_DOMAIN,
                SERVICE_GET_FORECASTS,
                {
                    CONF_TYPE: forecast_type,
                    CONF_ENTITY_ID: self._weather_entity,
                },
                blocking=True,
                return_response=True,
            )
        except HomeAssistantError as ex:
            msg = "Can't get forecast data! Are you sure it's the weather provider?"
            raise HomeAssistantError(msg) from ex

        _LOGGER.debug("Current temperature %.1f°C", temp)

        today = dt_util.start_of_local_day()
        cur_date = today.strftime("%F")
        stop_date = datetime.fromtimestamp(
            today.timestamp() + 86400 * (self._days + 1),
            tz=dt_util.DEFAULT_TIME_ZONE,
        ).strftime("%F")

        _LOGGER.debug("Inspect weather forecast from %s till %s", cur_date, stop_date)
        temp = [self._temp2c(temp, tmpu)]
        for fcast in forecast[self._weather_entity]["forecast"]:
            fc_date = fcast.get(ATTR_FORECAST_TIME)
            if isinstance(fc_date, int):
                fc_date = dt_util.as_local(
                    datetime.fromtimestamp(fc_date / 1000, dt_util.UTC)
                ).strftime("%F")
            elif isinstance(fc_date, datetime):
                fc_date = dt_util.as_local(fc_date).strftime("%F")
            if fc_date < cur_date:
                continue
            if fc_date == stop_date:
                break

            tmin = fcast.get(ATTR_FORECAST_TEMP_LOW)
            tmax = fcast.get(ATTR_FORECAST_TEMP)

            if tmin is not None and fc_date != cur_date:
                temp.append(self._temp2c(tmin, tmpu))
            if tmax is not None:
                temp.append(self._temp2c(tmax, tmpu))

        _LOGGER.debug("Temperature vector: %s", temp)
        for i in temp:
            if i <= 0.5:  # noqa: PLR2004
                _LOGGER.debug("Too cold temperature detected!")
                self._attr_is_on = True
                return

        temp = sum(temp) / len(temp)
        _LOGGER.debug("Average temperature: %.1f°C", temp)
        self._attr_is_on = temp < (
            TEMP_CHANGE
            if self._attr_is_on is None
            else TEMP_CHANGE + TEMP_ERROR
            if self._attr_is_on is True
            else TEMP_CHANGE - TEMP_ERROR
        )
