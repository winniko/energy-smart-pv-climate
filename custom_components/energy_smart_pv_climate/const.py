"""Constants for the Energy Smart PV integration."""

DOMAIN = "energy_smart_pv"

# Configuration Keys
CONF_GRID_SENSOR = "grid_sensor"
CONF_BATTERY_SENSOR = "battery_sensor"
CONF_AC_POWER_SENSOR = "ac_power_sensor"
CONF_CLIMATE_AC = "climate_ac"
CONF_CLIMATE_HEATER = "climate_heater"
CONF_MIN_BATTERY_LEVEL = "min_battery_level"
CONF_EXPORT_THRESHOLD = "export_threshold"
CONF_SUMMER_TEMP = "summer_temp"
CONF_WINTER_TEMP = "winter_temp"
CONF_OUTDOOR_TEMP_SENSOR = "outdoor_temp_sensor"
CONF_OUTDOOR_HUMIDITY_SENSOR = "outdoor_humidity_sensor"
CONF_ADAPTIVE_OFFSET = "adaptive_offset"
CONF_BOOST_OFFSET = "boost_offset"
CONF_DISABLE_HEATER_IN_COOL = "disable_heater_in_cool"
CONF_HUMIDITY_THRESHOLD = "humidity_threshold"
CONF_AUTO_ACTIVE = "auto_active"
CONF_SHARED_DEHUM = "shared_dehumidification"
CONF_WINTER_DEHUM = "winter_dehumidification"

# Defaults
DEFAULT_MIN_BATTERY_LEVEL = 80
DEFAULT_EXPORT_THRESHOLD = 2000
DEFAULT_SUMMER_TEMP = 24.0
DEFAULT_WINTER_TEMP = 21.0
DEFAULT_ADAPTIVE_OFFSET = 7
DEFAULT_BOOST_OFFSET = 2
DEFAULT_DISABLE_HEATER_IN_COOL = False
DEFAULT_HUMIDITY_THRESHOLD = 60
DEFAULT_SHARED_DEHUM = False
DEFAULT_WINTER_DEHUM = False
