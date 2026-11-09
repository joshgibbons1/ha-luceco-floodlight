# Luceco Smart Floodlight for Home Assistant

Local control of Luceco smart PIR floodlights that are set up with the BG Home
app, such as the Smart Castra PIR security floodlight (model codes starting
`LSMFSP`). No cloud and no app needed once the floodlight is on your Wi-Fi.

> This is an unofficial project and is not affiliated with or endorsed by
> Luceco, BG Electrical or Broadlink. All product and company names belong to
> their owners.

## Why a separate integration?

Under the hood these floodlights use Broadlink's platform, but Home Assistant's
built-in Broadlink integration rejects them as "not supported", because the
floodlight's device type (`0x647a`) is missing from the Broadlink library.
The floodlight does speak the same local protocol as Broadlink's light bulbs,
so this integration reuses that part of the library and adds the floodlight's
own settings.

## Requirements

- Home Assistant 2026.10.2 or newer. This is the first release that uses the
  `broadlink-async` library. Home Assistant loads its built-in Broadlink
  integration as a dependency of this one to get that library. You do not need
  to add any Broadlink devices.
- A floodlight on your 2.4 GHz Wi-Fi that is not locked to the app (see
  [Troubleshooting](#troubleshooting)).

## Installation

**HACS:** add this repository as a custom repository (type: Integration),
install **Luceco Smart Floodlight**, then restart Home Assistant.

**Manual:** copy `custom_components/luceco_floodlight` into the
`custom_components` folder of your Home Assistant configuration, then restart.

## Getting the floodlight onto your Wi-Fi

You can set the floodlight up with the BG Home app, but the app locks the
device to itself soon after pairing, and a locked device refuses connections
from Home Assistant. On the unit this was developed with, that only worked if
the app was closed quickly after pairing, before it locked the device, which
was fiddly and unreliable. A more dependable route that skips the app
entirely is to put the floodlight on your Wi-Fi from a computer with the
`broadlink` Python package:

1. Put the floodlight into connection (pairing) mode. It has no buttons: it
   is wired through a switch (for example a fused spur), and the installation
   manual says that switch is used to start connection mode. On the unit this
   was developed with, switching the power off and on five times in a row made
   the PIR sensor flash red, and the floodlight then created its own temporary
   Wi-Fi network. Check your manual if yours behaves differently.
2. Join that network from a laptop or PC.
3. Run the setup, with your own network name and password. The last number is
   the security mode: 0 none, 1 WEP, 2 WPA1, 3 WPA2, 4 WPA1/2.

   ```bash
   python3 -m venv broadlink-setup      # on Debian/Ubuntu: sudo apt install python3-venv
   broadlink-setup/bin/pip install broadlink
   broadlink-setup/bin/python -c "import broadlink; broadlink.setup('YOUR_WIFI_NAME', 'YOUR_WIFI_PASSWORD', 3)"
   ```

4. Reconnect your computer to your normal Wi-Fi. The floodlight joins your
   network.

> **Do this on a separate computer, not inside the Home Assistant container or
> its Python environment.** Installing the classic `broadlink` package there
> can overwrite the library that Home Assistant's own Broadlink integration
> uses and break it.

Give the floodlight a fixed IP address (for example a DHCP reservation in your
router) so it does not change.

## Setup in Home Assistant

Go to **Settings → Devices & services → Add integration → Luceco Smart
Floodlight** and enter the floodlight's IP address. If the address changes
later, use **Reconfigure** on the integration entry.

## Entities

| Entity | Type | Description |
| --- | --- | --- |
| Luceco Floodlight | light | On, off and brightness. Uses the device's manual mode (see below). |
| Mode | select | Sensor, Manual, Dusk to dawn or Night glow. |
| Sensor active when | select | Night, Dusk or Day: how dark it must be before the sensor may switch the light on. Day makes it work in daylight. |
| Light brightness | number | LED brightness, 0–100 %, used in every mode. |
| Sensitivity | number | 0 (least sensitive) to 3 (most sensitive). |
| Light on time | number | Seconds the light stays on after motion, 10–1800. |
| Motion | binary sensor | PIR trigger, held for the on time. Only active when it is dark enough for the sensor. |
| Ambient light level | sensor | Diagnostic, 0 (night) to 3 (day), read by the floodlight's photocell. |

### Modes

- **Sensor**: the light switches on with motion and off after the on time.
- **Manual**: the light is on or off, controlled by the light entity.
- **Dusk to dawn**: the light stays on while it is dark.
- **Night glow**: a dim glow at 10 % that goes to full brightness on motion.

### Turning the light off

Like the app's power button, the light entity works through Manual mode:
turning it on switches to Manual with the light on, turning it off switches to
Manual with the light off. Manual off keeps the sensor from lighting the
floodlight until you pick another mode, for example Sensor, from the **Mode**
select.

The light is reported as on while the main light is lit, including when the
sensor or Dusk to dawn lit it. Night glow is not reported as on.

## Example: light on for five minutes, then back to the sensor

```yaml
actions:
  - action: light.turn_on
    target:
      entity_id: light.luceco_floodlight
  - delay: "00:05:00"
  - action: select.select_option
    target:
      entity_id: select.luceco_floodlight_mode
    data:
      option: sensor
```

Entity IDs follow the name you give the device, so adjust them to match.

## Troubleshooting

- **Cannot connect during setup:** check the IP address, and that the
  floodlight is not locked to the app. Removing it from the BG Home app, or
  unlocking it in the device settings there, fixes that.
- **Motion never triggers in daylight:** that is the **Sensor active when**
  setting. Set it to Day to make the sensor work in daylight.

## How it works

The integration polls the floodlight every 3 seconds over the local network
(UDP). It reads and writes these keys of the device's JSON state:

| Key | Meaning |
| --- | --- |
| `mode_switch` | 0 sensor, 5 manual, 6 dusk to dawn, 7 night glow |
| `lightpwr` | Manual on/off, only used in Manual mode |
| `brightness` | LED brightness, 0–100 |
| `sensitivity_en` | Sensor sensitivity, 0–3 |
| `Delay time` | On time in seconds, 10–1800 |
| `Brightness control` | Ambient light threshold: 5 night, 100 dusk, 2000 day |
| `lmstatus` | Ambient light level, 0 night to 3 day (read-only) |
| `pir_detected` | Sensor trigger |
| `ifttt_enable` | Set while the main light is lit |

The device also accepts `mode_switch` values 3, 4 and 8. They are not
exposed, as no useful behaviour was found for them.

## Limitations

- Tested with one floodlight. Other variants may differ.
- There is no automatic discovery yet. Add the device by IP address.

## Acknowledgements

The local protocol knowledge comes from the
[python-broadlink](https://github.com/mjg59/python-broadlink) project.
