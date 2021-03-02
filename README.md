*Please :star: this repo if you find it useful*

# Snowtire Binary Sensor for Home Assistant

[![GitHub Release](https://img.shields.io/github/tag-date/Limych/ha-snowtire?label=release&style=popout)](https://github.com/Limych/ha-snowtire/releases)
[![GitHub Activity](https://img.shields.io/github/commit-activity/y/Limych/ha-snowtire.svg?style=popout)](https://github.com/Limych/ha-snowtire/commits/master)
[![License](https://img.shields.io/badge/license-Creative_Commons_BY--NC--SA_License-lightgray.svg?style=popout)](LICENSE.md)
![Requires.io](https://img.shields.io/requires/github/Limych/ha-snowtire)

[![hacs](https://img.shields.io/badge/HACS-Default-orange.svg?style=popout)][hacs]
![Project Maintenance](https://img.shields.io/badge/maintainer-Andrey%20Khrolenok%20%40Limych-blue.svg?style=popout)

[![GitHub pull requests](https://img.shields.io/github/issues-pr/Limych/ha-snowtire?style=popout)](https://github.com/Limych/ha-snowtire/pulls)
[![Bugs](https://img.shields.io/github/issues/Limych/ha-snowtire/bug.svg?colorB=red&label=bugs&style=popout)](https://github.com/Limych/ha-snowtire/issues?q=is%3Aopen+is%3Aissue+label%3ABug)

[![Community Forum](https://img.shields.io/badge/community-forum-brightgreen.svg?style=popout)][forum-support]

This component checks the weather forecast for several days in advance and concludes whether it is time to change car tires from summer to winter and vice versa.

![Example](example.jpg)

> **_Note_**:\
> You can find a real example of using this component in [my Home Assistant configuration](https://github.com/Limych/HomeAssistantConfiguration).

I also suggest you [visit the support topic][forum-support] on the community forum.

## Installation

### HACS - Recommended

1. Have [HACS](https://hacs.xyz) installed, this will allow you to easily manage and track updates.
1. Search for "Snowtire Sensor".
1. Click Install below the found integration.
1. Configure using the configuration instructions below.
1. Restart Home-Assistant.

### Manual

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `snowtire`.
4. Download file `snowtire.zip` from the [latest release section][latest-release] in this repository.
5. Extract _all_ files from this archive you downloaded in the directory (folder) `snowtire` you created.
1. Add `snowtire` sensor to your `configuration.yaml` file:

    ```yaml
    # Example configuration.yaml entry
    binary_sensor:
      - platform: snowtire
        weather: weather.gismeteo_daily
    ```

1. Restart Home Assistant

This sensor should work with any weather provider in any of it settings. But please note that the sensor cannot see further than the weather provider shows. Therefore, it is recommended to set the `daily` mode in the weather provider settings. If necessary, you can configure a separate weather provider instance especially for this sensor.

> **_Note_**:\
> Unfortunately, the binary sensor can show only two states — “on” and “off”.
> In the case of this sensor, “on” should be interpreted as *“it is time to set **winter** tires to the car”*, and “off” — as *“it is time to set **summer** tires to the car”*.

<p align="center">* * *</p>
I put a lot of work into making this repo and component available and updated to inspire and help others! I will be glad to receive thanks from you — it will give me new strength and add enthusiasm:
<p align="center"><br>
<a href="https://www.patreon.com/join/limych?" target="_blank"><img src="http://khrolenok.ru/support_patreon.png" alt="Patreon" width="250" height="48"></a>
<br>or&nbsp;support via Bitcoin or Etherium:<br>
<a href="https://sochain.com/a/mjz640g" target="_blank"><img src="http://khrolenok.ru/support_bitcoin.png" alt="Bitcoin" width="150"><br>
16yfCfz9dZ8y8yuSwBFVfiAa3CNYdMh7Ts</a>
</p>

### Configuration Variables

**weather:**\
  _(string) (Required)_\
  Weather provider entity ID.

**name:**\
  _(string) (Optional)_\
  Name to use in the frontend.\
  _Default value: 'Snowtire'_

**days:**\
  _(integer) (Optional)_\
  The number of days how far forward the sensor looks for the weather forecast.\
  _Default value: 7_

## Track updates

You can automatically track new versions of this component and update it by [HACS][hacs].

## Contributions are welcome!

This is an active open-source project. We are always open to people who want to
use the code or contribute to it.

We have set up a separate document containing our
[contribution guidelines](CONTRIBUTING.md).

Thank you for being involved! :heart_eyes:

## Authors & contributors

The original setup of this component is by [Andrey "Limych" Khrolenok][limych].

For a full list of all authors and contributors,
check [the contributor's page][contributors].

## License

creative commons Attribution-NonCommercial-ShareAlike 4.0 International License

See separate [license file](LICENSE.md) for full text.

[forum-support]: https://community.home-assistant.io/t/car-wash-binary-sensor/110046
[hacs]: https://github.com/custom-components/hacs
[limych]: https://github.com/Limych
[contributors]: https://github.com/Limych/ha-snowtire/graphs/contributors
