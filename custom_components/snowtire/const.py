"""
The Snowtire binary sensor.

For more details about this platform, please refer to the documentation at
https://github.com/Limych/ha-snowtire/
"""

from typing import Final

from homeassistant.const import Platform

# Base component constants
NAME: Final = "Snowtire Sensor"
DOMAIN: Final = "snowtire"
VERSION: Final = "1.6.0"
ISSUE_URL: Final = "https://github.com/Limych/ha-snowtire/issues"
#
DOMAIN_YAML: Final = f"_yaml_{DOMAIN}"

STARTUP_MESSAGE: Final = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have ANY issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""

# Platforms
PLATFORMS: Final = [Platform.BINARY_SENSOR]

# Icons
ICON_WINTER: Final = "mdi:snowflake"
ICON_SUMMER: Final = "mdi:white-balance-sunny"

# Configuration and options
CONF_WEATHER: Final = "weather"
CONF_DAYS: Final = "days"
CONF_CREATE_NOTIFICATIONS: Final = "create_notifications"

# Defaults
DEFAULT_DAYS: Final = 7
DEFAULT_CREATE_NOTIFICATIONS: Final = True
