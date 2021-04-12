*Please :star: this repo if you find it useful*

# Snowtire Binary Sensor for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]][license]

[![hacs][hacs-shield]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]

[![Community Forum][forum-shield]][forum]

_This component checks the weather forecast for several days in advance and concludes whether it is time to change car tires from summer to winter and vice versa._

![Example][exampleimg]

I also suggest you [visit the support topic][forum] on the community forum.

## Installation

### Install from HACS (recommended)

1. Have [HACS][hacs] installed, this will allow you to easily manage and track updates.
1. Search for "Snowtire".
1. Click Install below the found integration.
1. _If you want to configure component via Home Assistant UI..._\
    in the HA UI add Snowtire sensor into system.
1. _If you want to configure component via `configuration.yaml`..._\
    follow instructions below, then restart Home Assistant.

### Manual installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `snowtire`.
1. Download file `snowtire.zip` from the [latest release section][releases-latest] in this repository.
1. Extract _all_ files from this archive you downloaded in the directory (folder) you created.
1. Restart Home Assistant
1. _If you want to configure component via Home Assistant UI..._\
    in the HA UI add Snowtire sensor into system.
1. _If you want to configure component via `configuration.yaml`..._\
    follow instructions below, then restart Home Assistant.

## Configuration Example

```yaml
# Example configuration.yaml entry
binary_sensor:
  - platform: snowtire
    weather: weather.gismeteo_daily
```

<p align="center">* * *</p>
I put a lot of work into making this repo and component available and updated to inspire and help others! I will be glad to receive thanks from you — it will give me new strength and add enthusiasm:
<p align="center"><br>
<a href="https://www.patreon.com/join/limych?" target="_blank"><img src="http://khrolenok.ru/support_patreon.png" alt="Patreon" width="250" height="48"></a>
<br>or&nbsp;support via Bitcoin or Etherium:<br>
<a href="https://sochain.com/a/mjz640g" target="_blank"><img src="http://khrolenok.ru/support_bitcoin.png" alt="Bitcoin" width="150"><br>
16yfCfz9dZ8y8yuSwBFVfiAa3CNYdMh7Ts</a>
</p>

### Configuration Variables

> **_Note_**:\
> This sensor should work with any weather provider in any of it settings. But please note that the sensor cannot see further than the weather provider shows. Therefore, it is recommended to set the `daily` mode in the weather provider settings. If necessary, you can configure a separate weather provider instance especially for this sensor.

**weather:**\
  _(string) (Required)_\
  Weather provider entity ID.

**name:**\
  _(string) (Optional) (Default value: "Snowtire")_\
  Name to use in the frontend.

**days:**\
  _(positive integer) (Optional) (Default value: 7)_\
  The number of days how far forward the sensor looks for the weather forecast.

## Track updates

You can automatically track new versions of this component and update it by [HACS][hacs].

## Troubleshooting

To enable debug logs use this configuration:
```yaml
# Example configuration.yaml entry
logger:
  default: info
  logs:
    custom_components.snowtire: debug
```
... then restart HA.

## Contributions are welcome!

This is an active open-source project. We are always open to people who want to use the code or contribute to it.

We have set up a separate document containing our [contribution guidelines](CONTRIBUTING.md).

Thank you for being involved! :heart_eyes:

## Authors & contributors

The original setup of this component is by [Andrey "Limych" Khrolenok](https://github.com/Limych).

For a full list of all authors and contributors, check [the contributor's page][contributors].

## License

creative commons Attribution-NonCommercial-ShareAlike 4.0 International License

See separate [license file](LICENSE.md) for full text.

***

[component]: https://github.com/Limych/ha-snowtire
[commits-shield]: https://img.shields.io/github/commit-activity/y/Limych/ha-snowtire.svg?style=popout
[commits]: https://github.com/Limych/ha-snowtire/commits/dev
[hacs-shield]: https://img.shields.io/badge/HACS-Default-orange.svg?style=popout
[hacs]: https://hacs.xyz
[exampleimg]: https://github.com/Limych/ha-snowtire/raw/dev/example.jpg
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=popout
[forum]: https://community.home-assistant.io/t/snowtire-sensor/286111
[license]: https://github.com/Limych/ha-snowtire/blob/main/LICENSE.md
[license-shield]: https://img.shields.io/badge/license-Creative_Commons_BY--NC--SA_License-lightgray.svg?style=popout
[maintenance-shield]: https://img.shields.io/badge/maintainer-Andrey%20Khrolenok%20%40Limych-blue.svg?style=popout
[releases-shield]: https://img.shields.io/github/release/Limych/ha-snowtire.svg?style=popout
[releases]: https://github.com/Limych/ha-snowtire/releases
[releases-latest]: https://github.com/Limych/ha-snowtire/releases/latest
[user_profile]: https://github.com/Limych
[report_bug]: https://github.com/Limych/ha-snowtire/issues/new?template=bug_report.md
[suggest_idea]: https://github.com/Limych/ha-snowtire/issues/new?template=feature_request.md
[contributors]: https://github.com/Limych/ha-snowtire/graphs/contributors
