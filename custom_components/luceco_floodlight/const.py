"""Constants for the Luceco Floodlight integration."""

DOMAIN = "luceco_floodlight"

SCAN_INTERVAL_SECONDS = 3

# Keys in the device's JSON state, found by probing the device and by watching
# its state while operating the vendor app.
KEY_POWER = "lightpwr"  # manual on/off, only used in manual mode
KEY_BRIGHTNESS = "brightness"  # LED brightness, 0-100
KEY_MODE = "mode_switch"
KEY_SENSITIVITY = "sensitivity_en"  # 0 (least sensitive) to 3 (most sensitive)
KEY_ON_TIME = "Delay time"  # seconds the light stays on after motion, 10-1800
KEY_LIGHT_LEVEL = "Brightness control"  # ambient light threshold for the sensor
KEY_AMBIENT = "lmstatus"  # ambient light at the photocell, 0 night to 3 day
KEY_MOTION = "pir_detected"  # set on a sensor trigger, held for the on time
KEY_LIGHT_LIT = "ifttt_enable"  # set while the main light is lit

# Values of KEY_MODE.
MODE_SENSOR = 0
MODE_MANUAL = 5
MODE_DUSK_TO_DAWN = 6
MODE_NIGHT_GLOW = 7

# Values of KEY_LIGHT_LEVEL used by the vendor app's presets.
LEVEL_NIGHT = 5
LEVEL_DUSK = 100
LEVEL_DAY = 2000
