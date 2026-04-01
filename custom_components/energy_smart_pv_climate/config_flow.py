"""Config flow for Energy Smart PV integration."""
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_GRID_SENSOR,
    CONF_BATTERY_SENSOR,
    CONF_CLIMATE_AC,
    CONF_CLIMATE_HEATER,
    CONF_MIN_BATTERY_LEVEL,
    CONF_EXPORT_THRESHOLD,
    CONF_SUMMER_TEMP,
    CONF_WINTER_TEMP,
    CONF_OUTDOOR_TEMP_SENSOR,
    CONF_OUTDOOR_HUMIDITY_SENSOR,
    CONF_AC_POWER_SENSOR,
    CONF_ADAPTIVE_OFFSET,
    CONF_BOOST_OFFSET,
    CONF_DISABLE_HEATER_IN_COOL,
    CONF_HUMIDITY_THRESHOLD,
    CONF_SHARED_DEHUM,
    CONF_WINTER_DEHUM,
    DEFAULT_MIN_BATTERY_LEVEL,
    DEFAULT_EXPORT_THRESHOLD,
    DEFAULT_SUMMER_TEMP,
    DEFAULT_WINTER_TEMP,
    DEFAULT_ADAPTIVE_OFFSET,
    DEFAULT_BOOST_OFFSET,
    DEFAULT_DISABLE_HEATER_IN_COOL,
    DEFAULT_HUMIDITY_THRESHOLD,
    DEFAULT_SHARED_DEHUM,
    DEFAULT_WINTER_DEHUM,
)

_LOGGER = logging.getLogger(__name__)

class EnergySmartPVConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Energy Smart PV."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        existing_entries = self._async_current_entries()
        first_data = existing_entries[0].data if existing_entries else {}

        if user_input is not None:
            title = user_input.get("name", "Energy Smart PV Zone")
            data = dict(user_input)
            if first_data:
                data[CONF_GRID_SENSOR] = first_data.get(CONF_GRID_SENSOR)
                if CONF_BATTERY_SENSOR in first_data:
                    data[CONF_BATTERY_SENSOR] = first_data.get(CONF_BATTERY_SENSOR)
                if CONF_OUTDOOR_TEMP_SENSOR in first_data:
                    data[CONF_OUTDOOR_TEMP_SENSOR] = first_data.get(CONF_OUTDOOR_TEMP_SENSOR)
                if CONF_OUTDOOR_HUMIDITY_SENSOR in first_data:
                    data[CONF_OUTDOOR_HUMIDITY_SENSOR] = first_data.get(CONF_OUTDOOR_HUMIDITY_SENSOR)
                if CONF_AC_POWER_SENSOR in first_data:
                    data[CONF_AC_POWER_SENSOR] = first_data.get(CONF_AC_POWER_SENSOR)
            return self.async_create_entry(title=title, data=data)

        grid_suggested = first_data.get(CONF_GRID_SENSOR)
        battery_suggested = first_data.get(CONF_BATTERY_SENSOR)
        outdoor_suggested = first_data.get(CONF_OUTDOOR_TEMP_SENSOR)
        outdoor_humidity_suggested = first_data.get(CONF_OUTDOOR_HUMIDITY_SENSOR)
        ac_power_suggested = first_data.get(CONF_AC_POWER_SENSOR)

        if existing_entries:
            data_schema = vol.Schema(
                {
                    vol.Required("name", default="Soggiorno"): str,
                    vol.Required(CONF_CLIMATE_AC): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="climate", multiple=False)
                    ),
                    vol.Optional(CONF_CLIMATE_HEATER): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="climate", multiple=False)
                    ),
                    vol.Required(
                        CONF_EXPORT_THRESHOLD, default=DEFAULT_EXPORT_THRESHOLD
                    ): vol.All(vol.Coerce(int), vol.Range(min=0)),
                    vol.Required(
                        CONF_MIN_BATTERY_LEVEL, default=DEFAULT_MIN_BATTERY_LEVEL
                    ): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
                    vol.Required(
                        CONF_SUMMER_TEMP, default=DEFAULT_SUMMER_TEMP
                    ): vol.All(vol.Coerce(float), vol.Range(min=16, max=32)),
                    vol.Required(
                        CONF_WINTER_TEMP, default=DEFAULT_WINTER_TEMP
                    ): vol.All(vol.Coerce(float), vol.Range(min=16, max=32)),
                    vol.Optional(
                        CONF_HUMIDITY_THRESHOLD, default=DEFAULT_HUMIDITY_THRESHOLD
                    ): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
                }
            )
        else:
            data_schema = vol.Schema(
                {
                    vol.Required("name", default="Soggiorno"): str,
                    vol.Required(
                        CONF_GRID_SENSOR,
                        description={"suggested_value": grid_suggested} if grid_suggested else {},
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="sensor")
                    ),
                    vol.Optional(
                        CONF_BATTERY_SENSOR,
                        description={"suggested_value": battery_suggested} if battery_suggested else {},
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="sensor")
                    ),
                    vol.Optional(
                        CONF_OUTDOOR_TEMP_SENSOR,
                        description={"suggested_value": outdoor_suggested} if outdoor_suggested else {},
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="sensor")
                    ),
                    vol.Optional(
                        CONF_OUTDOOR_HUMIDITY_SENSOR,
                        description={"suggested_value": outdoor_humidity_suggested} if outdoor_humidity_suggested else {},
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="sensor")
                    ),
                    vol.Optional(
                        CONF_AC_POWER_SENSOR,
                        description={"suggested_value": ac_power_suggested} if ac_power_suggested else {},
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="sensor")
                    ),
                    vol.Optional(
                        CONF_OUTDOOR_HUMIDITY_SENSOR,
                        description={"suggested_value": outdoor_humidity_suggested} if outdoor_humidity_suggested else {},
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="sensor")
                    ),
                    vol.Required(CONF_CLIMATE_AC): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="climate", multiple=False)
                    ),
                    vol.Optional(CONF_CLIMATE_HEATER): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="climate", multiple=False)
                    ),
                    vol.Required(
                        CONF_EXPORT_THRESHOLD, default=DEFAULT_EXPORT_THRESHOLD
                    ): vol.All(vol.Coerce(int), vol.Range(min=0)),
                    vol.Required(
                        CONF_MIN_BATTERY_LEVEL, default=DEFAULT_MIN_BATTERY_LEVEL
                    ): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
                    vol.Required(
                        CONF_SUMMER_TEMP, default=DEFAULT_SUMMER_TEMP
                    ): vol.All(vol.Coerce(float), vol.Range(min=16, max=32)),
                    vol.Required(
                        CONF_WINTER_TEMP, default=DEFAULT_WINTER_TEMP
                    ): vol.All(vol.Coerce(float), vol.Range(min=16, max=32)),
                    vol.Optional(
                        CONF_HUMIDITY_THRESHOLD, default=DEFAULT_HUMIDITY_THRESHOLD
                    ): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
                }
            )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)

class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for the component."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        # In newer Home Assistant versions, `config_entry` is a read-only property.
        # Store the entry in the internal attribute used by the base class.
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}

        try:
            if user_input is not None:
                return self.async_create_entry(title="", data=user_input)

            def get_value(key, default):
                if self.config_entry.options and key in self.config_entry.options:
                    return self.config_entry.options[key]
                if self.config_entry.data and key in self.config_entry.data:
                    return self.config_entry.data[key]
                return default

            export_val = get_value(CONF_EXPORT_THRESHOLD, DEFAULT_EXPORT_THRESHOLD)
            battery_val = get_value(CONF_MIN_BATTERY_LEVEL, DEFAULT_MIN_BATTERY_LEVEL)
            summer_val = get_value(CONF_SUMMER_TEMP, DEFAULT_SUMMER_TEMP)
            winter_val = get_value(CONF_WINTER_TEMP, DEFAULT_WINTER_TEMP)
            adaptive_val = get_value(CONF_ADAPTIVE_OFFSET, DEFAULT_ADAPTIVE_OFFSET)
            boost_val = get_value(CONF_BOOST_OFFSET, DEFAULT_BOOST_OFFSET)
            disable_heater_in_cool_val = get_value(CONF_DISABLE_HEATER_IN_COOL, DEFAULT_DISABLE_HEATER_IN_COOL)
            outdoor_val = get_value(CONF_OUTDOOR_TEMP_SENSOR, None)
            outdoor_humidity_val = get_value(CONF_OUTDOOR_HUMIDITY_SENSOR, None)
            ac_power_val = get_value(CONF_AC_POWER_SENSOR, None)
            humidity_val = get_value(CONF_HUMIDITY_THRESHOLD, DEFAULT_HUMIDITY_THRESHOLD)
            shared_dehum_val = get_value(CONF_SHARED_DEHUM, DEFAULT_SHARED_DEHUM)
            winter_dehum_val = get_value(CONF_WINTER_DEHUM, DEFAULT_WINTER_DEHUM)

            schema = {
                vol.Optional(CONF_EXPORT_THRESHOLD, default=export_val): vol.All(vol.Coerce(int), vol.Range(min=0)),
                vol.Optional(CONF_MIN_BATTERY_LEVEL, default=battery_val): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
                vol.Optional(CONF_SUMMER_TEMP, default=summer_val): vol.All(vol.Coerce(float), vol.Range(min=16, max=32)),
                vol.Optional(CONF_WINTER_TEMP, default=winter_val): vol.All(vol.Coerce(float), vol.Range(min=16, max=32)),
                vol.Optional(CONF_ADAPTIVE_OFFSET, default=adaptive_val): vol.All(vol.Coerce(int), vol.Range(min=0, max=30)),
                vol.Optional(CONF_BOOST_OFFSET, default=boost_val): vol.All(vol.Coerce(int), vol.Range(min=0, max=10)),
                vol.Optional(CONF_SHARED_DEHUM, default=shared_dehum_val): cv.boolean,
                vol.Optional(CONF_WINTER_DEHUM, default=winter_dehum_val): cv.boolean,
                vol.Optional(CONF_DISABLE_HEATER_IN_COOL, default=disable_heater_in_cool_val): cv.boolean,
                vol.Optional(CONF_HUMIDITY_THRESHOLD, default=humidity_val): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
            }

            # IMPORTANT: never force a default into an entity selector (some HA builds crash)
            # If the user already had a value, HA will show it anyway in most cases.
            schema[vol.Optional(CONF_OUTDOOR_TEMP_SENSOR)] = selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor")
            )
            schema[vol.Optional(CONF_OUTDOOR_HUMIDITY_SENSOR)] = selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor")
            )
            schema[vol.Optional(CONF_AC_POWER_SENSOR)] = selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor")
            )

            return self.async_show_form(step_id="init", data_schema=vol.Schema(schema), errors=errors)
        except Exception as err:
            _LOGGER.exception("Options flow crashed for entry %s: %s", getattr(self.config_entry, "entry_id", "?"), err)
            errors["base"] = "unknown"
            schema = {
                vol.Optional(CONF_EXPORT_THRESHOLD, default=DEFAULT_EXPORT_THRESHOLD): vol.All(vol.Coerce(int), vol.Range(min=0)),
                vol.Optional(CONF_MIN_BATTERY_LEVEL, default=DEFAULT_MIN_BATTERY_LEVEL): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
                vol.Optional(CONF_SUMMER_TEMP, default=DEFAULT_SUMMER_TEMP): vol.All(vol.Coerce(float), vol.Range(min=16, max=32)),
                vol.Optional(CONF_WINTER_TEMP, default=DEFAULT_WINTER_TEMP): vol.All(vol.Coerce(float), vol.Range(min=16, max=32)),
            }
            return self.async_show_form(step_id="init", data_schema=vol.Schema(schema), errors=errors)
