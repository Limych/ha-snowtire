"""
The Snowtire binary sensor.

For more details about this platform, please refer to the documentation at
https://github.com/Limych/ha-snowtire/
"""

#  Copyright (c) 2024, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)

import logging

import voluptuous as vol
from homeassistant.components.weather import (
    DOMAIN as WEATHER_DOMAIN,
)
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import CONF_NAME, CONF_UNIQUE_ID
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from custom_components.snowtire.const import (
    CONF_CREATE_NOTIFICATIONS,
    CONF_DAYS,
    CONF_WEATHER,
    DEFAULT_CREATE_NOTIFICATIONS,
    DEFAULT_DAYS,
    DOMAIN,
    DOMAIN_YAML,
    PLATFORMS,
    STARTUP_MESSAGE,
)

_LOGGER = logging.getLogger(__name__)

SNOWTIRE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_WEATHER): cv.entity_domain(WEATHER_DOMAIN),
        vol.Optional(CONF_NAME): cv.string,
        vol.Optional(CONF_DAYS, default=DEFAULT_DAYS): cv.positive_int,
        vol.Optional(
            CONF_CREATE_NOTIFICATIONS, default=DEFAULT_CREATE_NOTIFICATIONS
        ): bool,
        vol.Optional(CONF_UNIQUE_ID): cv.string,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: vol.All(cv.ensure_list, [SNOWTIRE_SCHEMA])}, extra=vol.ALLOW_EXTRA
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up component."""
    if DOMAIN not in hass.data:
        _LOGGER.info(STARTUP_MESSAGE)
        hass.data.setdefault(DOMAIN, {})

    if DOMAIN not in config:
        return True

    hass.data[DOMAIN_YAML] = config[DOMAIN]
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_IMPORT}, data={}
        )
    )

    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set the config entry up."""
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    # Reload entry when its updated.
    config_entry.async_on_unload(config_entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)
    return True


async def async_reload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Reload the config entry when it changed."""
    await hass.config_entries.async_reload(config_entry.entry_id)
