"""
Config flow for the Snowtire integration.

For more details about this platform, please refer to the documentation at
https://github.com/Limych/ha-snowtire/
"""

#  Copyright (c) 2024, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Final

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.weather import DOMAIN as DOMAIN_WEATHER
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers import selector

if TYPE_CHECKING:
    from homeassistant.helpers.typing import ConfigType

from custom_components.snowtire.const import (
    CONF_CREATE_NOTIFICATIONS,
    CONF_DAYS,
    CONF_WEATHER,
    DEFAULT_CREATE_NOTIFICATIONS,
    DEFAULT_DAYS,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


OPTIONS_SCHEMA: Final = vol.Schema(
    {
        vol.Required(CONF_WEATHER): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=[DOMAIN_WEATHER])
        ),
        vol.Optional(CONF_DAYS, default=DEFAULT_DAYS): cv.positive_int,
        vol.Optional(
            CONF_CREATE_NOTIFICATIONS, default=DEFAULT_CREATE_NOTIFICATIONS
        ): bool,
    }
)


class SnowtireFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Snowtire integration."""

    VERSION = 1

    def __init__(self) -> None:
        """Init config flow."""
        self._errors = {}

    async def async_step_import(
        self, platform_config: ConfigType
    ) -> config_entries.ConfigFlowResult:
        """
        Import a config entry.

        Special type of import, we're not actually going to store any data.
        Instead, we're going to rely on the values that are in config file.
        """
        if self._async_current_entries():
            return self.async_abort(reason="no_mixed_config")

        return self.async_create_entry(title="configuration.yaml", data=platform_config)

    async def async_step_user(
        self, user_input: ConfigType = None
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        for entry in self._async_current_entries():
            if entry.source == config_entries.SOURCE_IMPORT:
                return self.async_abort(reason="no_mixed_config")

        self._errors = {}

        if user_input is not None:
            keys = [CONF_NAME]
            data = {key: user_input[key] for key in keys}
            options = {key: user_input[key] for key in user_input if key not in keys}
            return self.async_create_entry(
                title=user_input[CONF_NAME], data=data, options=options
            )

        schema = vol.Schema(
            {
                vol.Optional(CONF_NAME, default=self.hass.config.location_name): str,
            }
        ).extend(OPTIONS_SCHEMA.schema)
        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=self._errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get component options flow."""
        return SnowtireOptionsFlowHandler(config_entry)


class SnowtireOptionsFlowHandler(config_entries.OptionsFlow):
    """Config flow options handler."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize HACS options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(
        self,
        user_input: ConfigType = None,  # noqa: ARG002
    ) -> config_entries.ConfigFlowResult:  # pylint: disable=unused-argument
        """Manage the options."""
        if self.config_entry.source == config_entries.SOURCE_IMPORT:
            return self.async_abort(reason="no_options_available")

        return await self.async_step_user()

    async def async_step_user(
        self, user_input: ConfigType = None
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        if user_input is not None:
            self.options.update(user_input)
            return self.async_create_entry(
                title=self.config_entry.data.get(CONF_NAME), data=self.options
            )

        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(
                OPTIONS_SCHEMA,
                self.config_entry.options,
            ),
            description_placeholders={
                "name": self.config_entry.title,
            },
        )
