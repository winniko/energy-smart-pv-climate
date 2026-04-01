"""The Energy Smart PV integration."""
import logging
import asyncio
from datetime import timedelta
from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN, ATTR_ENTITY_ID
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    CONF_GRID_SENSOR,
    CONF_BATTERY_SENSOR,
    CONF_AC_POWER_SENSOR,
    CONF_CLIMATE_AC,
    CONF_CLIMATE_HEATER,
    CONF_MIN_BATTERY_LEVEL,
    CONF_EXPORT_THRESHOLD,
    CONF_SUMMER_TEMP,
    CONF_WINTER_TEMP,
    CONF_OUTDOOR_TEMP_SENSOR,
    CONF_OUTDOOR_HUMIDITY_SENSOR,
    CONF_ADAPTIVE_OFFSET,
    CONF_BOOST_OFFSET,
    CONF_DISABLE_HEATER_IN_COOL,
    CONF_HUMIDITY_THRESHOLD,
    CONF_AUTO_ACTIVE,
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

PLATFORMS: list[str] = ["sensor", "switch", "select"]

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the component."""
    hass.data.setdefault(DOMAIN, {})
    
    async def _set_humidity_threshold(call):
        entry_id = call.data.get("entry_id")
        value = call.data.get("value")
        try:
            value = int(float(value))
        except Exception:
            _LOGGER.error("Invalid humidity threshold value: %s", value)
            return
        entry = hass.config_entries.async_get_entry(entry_id)
        if not entry:
            _LOGGER.error("Entry %s not found for humidity threshold update", entry_id)
            return
        options = dict(entry.options)
        options[CONF_HUMIDITY_THRESHOLD] = value
        hass.config_entries.async_update_entry(entry, options=options)
        await hass.config_entries.async_reload(entry.entry_id)

    async def _set_min_battery_level(call):
        entry_id = call.data.get("entry_id")
        value = call.data.get("value")
        try:
            value = int(float(value))
        except Exception:
            _LOGGER.error("Invalid min battery level value: %s", value)
            return
        entry = hass.config_entries.async_get_entry(entry_id)
        if not entry:
            _LOGGER.error("Entry %s not found for min battery level update", entry_id)
            return
        options = dict(entry.options)
        options[CONF_MIN_BATTERY_LEVEL] = value
        hass.config_entries.async_update_entry(entry, options=options)
        await hass.config_entries.async_reload(entry.entry_id)

    async def _set_export_threshold(call):
        entry_id = call.data.get("entry_id")
        value = call.data.get("value")
        try:
            value = int(float(value))
        except Exception:
            _LOGGER.error("Invalid export threshold value: %s", value)
            return
        entry = hass.config_entries.async_get_entry(entry_id)
        if not entry:
            _LOGGER.error("Entry %s not found for export threshold update", entry_id)
            return
        options = dict(entry.options)
        options[CONF_EXPORT_THRESHOLD] = value
        hass.config_entries.async_update_entry(entry, options=options)
        await hass.config_entries.async_reload(entry.entry_id)

    async def _set_summer_temp(call):
        entry_id = call.data.get("entry_id")
        value = call.data.get("value")
        try:
            value = float(value)
        except Exception:
            _LOGGER.error("Invalid summer temp value: %s", value)
            return
        entry = hass.config_entries.async_get_entry(entry_id)
        if not entry:
            _LOGGER.error("Entry %s not found for summer temp update", entry_id)
            return
        options = dict(entry.options)
        options[CONF_SUMMER_TEMP] = value
        hass.config_entries.async_update_entry(entry, options=options)
        await hass.config_entries.async_reload(entry.entry_id)

    async def _set_winter_temp(call):
        entry_id = call.data.get("entry_id")
        value = call.data.get("value")
        try:
            value = float(value)
        except Exception:
            _LOGGER.error("Invalid winter temp value: %s", value)
            return
        entry = hass.config_entries.async_get_entry(entry_id)
        if not entry:
            _LOGGER.error("Entry %s not found for winter temp update", entry_id)
            return
        options = dict(entry.options)
        options[CONF_WINTER_TEMP] = value
        hass.config_entries.async_update_entry(entry, options=options)
        await hass.config_entries.async_reload(entry.entry_id)

    async def _set_adaptive_offset(call):
        entry_id = call.data.get("entry_id")
        value = call.data.get("value")
        try:
            value = int(float(value))
        except Exception:
            _LOGGER.error("Invalid adaptive offset value: %s", value)
            return
        entry = hass.config_entries.async_get_entry(entry_id)
        if not entry:
            _LOGGER.error("Entry %s not found for adaptive offset update", entry_id)
            return
        options = dict(entry.options)
        options[CONF_ADAPTIVE_OFFSET] = value
        hass.config_entries.async_update_entry(entry, options=options)
        await hass.config_entries.async_reload(entry.entry_id)

    async def _set_boost_offset(call):
        entry_id = call.data.get("entry_id")
        value = call.data.get("value")
        try:
            value = int(float(value))
        except Exception:
            _LOGGER.error("Invalid boost offset value: %s", value)
            return
        entry = hass.config_entries.async_get_entry(entry_id)
        if not entry:
            _LOGGER.error("Entry %s not found for boost offset update", entry_id)
            return
        options = dict(entry.options)
        options[CONF_BOOST_OFFSET] = value
        hass.config_entries.async_update_entry(entry, options=options)
        await hass.config_entries.async_reload(entry.entry_id)

    async def _set_shared_dehum(call):
        entry_id = call.data.get("entry_id")
        raw = call.data.get("value")
        value = False
        if isinstance(raw, bool):
            value = raw
        elif isinstance(raw, (int, float)):
            value = raw != 0
        elif isinstance(raw, str):
            value = raw.strip().lower() in ("1", "true", "on", "yes", "y")
        entry = hass.config_entries.async_get_entry(entry_id)
        if not entry:
            _LOGGER.error("Entry %s not found for shared dehumidification update", entry_id)
            return
        options = dict(entry.options)
        options[CONF_SHARED_DEHUM] = value
        hass.config_entries.async_update_entry(entry, options=options)
        await hass.config_entries.async_reload(entry.entry_id)

    async def _set_winter_dehum(call):
        entry_id = call.data.get("entry_id")
        raw = call.data.get("value")
        value = False
        if isinstance(raw, bool):
            value = raw
        elif isinstance(raw, (int, float)):
            value = raw != 0
        elif isinstance(raw, str):
            value = raw.strip().lower() in ("1", "true", "on", "yes", "y")
        entry = hass.config_entries.async_get_entry(entry_id)
        if not entry:
            _LOGGER.error("Entry %s not found for winter dehumidification update", entry_id)
            return
        options = dict(entry.options)
        options[CONF_WINTER_DEHUM] = value
        hass.config_entries.async_update_entry(entry, options=options)
        await hass.config_entries.async_reload(entry.entry_id)

    hass.services.async_register(DOMAIN, "set_humidity_threshold", _set_humidity_threshold)
    hass.services.async_register(DOMAIN, "set_min_battery_level", _set_min_battery_level)
    hass.services.async_register(DOMAIN, "set_export_threshold", _set_export_threshold)
    hass.services.async_register(DOMAIN, "set_summer_temp", _set_summer_temp)
    hass.services.async_register(DOMAIN, "set_winter_temp", _set_winter_temp)
    hass.services.async_register(DOMAIN, "set_adaptive_offset", _set_adaptive_offset)
    hass.services.async_register(DOMAIN, "set_boost_offset", _set_boost_offset)
    hass.services.async_register(DOMAIN, "set_shared_dehumidification", _set_shared_dehum)
    hass.services.async_register(DOMAIN, "set_winter_dehumidification", _set_winter_dehum)
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from a config entry."""
    try:
        hass.data.setdefault(DOMAIN, {})

        _LOGGER.debug("Setting up Energy Smart PV for entry %s", entry.entry_id)

        manager = EnergySmartPVManager(hass, entry)
        hass.data[DOMAIN][entry.entry_id] = manager

        await manager.async_setup()
        
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        
        _LOGGER.info("Energy Smart PV setup successful for %s", entry.title)
        return True
    except Exception as e:
        _LOGGER.exception("Error setting up Energy Smart PV: %s", e)
        return False

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
        
    return unload_ok

class EnergySmartPVManager:
    """Class to manage the logic."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self.hass = hass
        self.entry = entry
        
        # Merge data and options
        self._config = {**entry.data, **entry.options}
        
        self._is_active = self._config.get(CONF_AUTO_ACTIVE, True)
        self._mode = "Auto"
        self._current_surplus = 0
        self._is_boosting = False
        self._battery_low = False
        self._battery_level = None
        self._ac_power = None
        self._last_boost_start = None
        self._last_boost_end = None
        
        # Hysteresis and Eco Mode
        self._low_surplus_since = None
        self._last_condition_check = None
        self._condition_met_since = None
        
        # Load config
        self._grid_sensor = self._config.get(CONF_GRID_SENSOR)
        self._battery_sensor = self._config.get(CONF_BATTERY_SENSOR)
        self._ac_power_sensor = self._config.get(CONF_AC_POWER_SENSOR)
        
        # New: Single Entity Logic
        self._ac_entity = self._config.get(CONF_CLIMATE_AC)
        self._heater_entity = self._config.get(CONF_CLIMATE_HEATER)
        
        # Compatibility fallback (if upgrading from old structure)
        # Ensure we always have a string or None, never a list
        if self._ac_entity and isinstance(self._ac_entity, list):
            if len(self._ac_entity) > 0:
                self._ac_entity = self._ac_entity[0]
            else:
                self._ac_entity = None
        
        elif not self._ac_entity and self._config.get("climate_ac"):
            val = self._config.get("climate_ac")
            if isinstance(val, list) and len(val) > 0:
                self._ac_entity = val[0]
            elif isinstance(val, str):
                self._ac_entity = val
                
        if self._heater_entity and isinstance(self._heater_entity, list):
            if len(self._heater_entity) > 0:
                self._heater_entity = self._heater_entity[0]
            else:
                self._heater_entity = None
                 
        elif not self._heater_entity and self._config.get("climate_heaters"):
            val = self._config.get("climate_heaters")
            if isinstance(val, list) and len(val) > 0:
                self._heater_entity = val[0]
            elif isinstance(val, str):
                self._heater_entity = val

        self._export_threshold = self._config.get(CONF_EXPORT_THRESHOLD, DEFAULT_EXPORT_THRESHOLD)
        self._min_battery_level = self._config.get(CONF_MIN_BATTERY_LEVEL, DEFAULT_MIN_BATTERY_LEVEL)
        self._summer_temp = self._config.get(CONF_SUMMER_TEMP, DEFAULT_SUMMER_TEMP)
        self._winter_temp = self._config.get(CONF_WINTER_TEMP, DEFAULT_WINTER_TEMP)
        self._outdoor_sensor = self._config.get(CONF_OUTDOOR_TEMP_SENSOR)
        self._outdoor_humidity_sensor = self._config.get(CONF_OUTDOOR_HUMIDITY_SENSOR)
        self._adaptive_offset = self._config.get(CONF_ADAPTIVE_OFFSET, DEFAULT_ADAPTIVE_OFFSET)
        self._boost_offset = self._config.get(CONF_BOOST_OFFSET, DEFAULT_BOOST_OFFSET)
        self._disable_heater_in_cool = self._config.get(CONF_DISABLE_HEATER_IN_COOL, DEFAULT_DISABLE_HEATER_IN_COOL)
        self._humidity_threshold = self._config.get(CONF_HUMIDITY_THRESHOLD, DEFAULT_HUMIDITY_THRESHOLD)
        self._shared_dehum = self._config.get(CONF_SHARED_DEHUM, DEFAULT_SHARED_DEHUM)
        self._winter_dehum = self._config.get(CONF_WINTER_DEHUM, DEFAULT_WINTER_DEHUM)
        self._current_humidity = None
        self._is_dehumidifying = False
        self._is_syncing = False  # Prevent recursion loops
        
        # New properties for card visibility
        self._is_eco_mode = False
        self._current_temp_ac = None
        self._current_temp_heater = None
        self._manual_lock_until = None
        
        # Linked Control Entities
        self._switch_entity_id = None
        self._select_entity_id = None

    def set_switch_entity(self, entity_id):
        self._switch_entity_id = entity_id
        
    def set_select_entity(self, entity_id):
        self._select_entity_id = entity_id
        
    @property
    def switch_entity_id(self):
        return self._switch_entity_id
        
    @property
    def select_entity_id(self):
        return self._select_entity_id

    @property
    def outdoor_sensor(self):
        return self._outdoor_sensor

    @property
    def outdoor_humidity_sensor(self):
        return self._outdoor_humidity_sensor
    
    @property
    def min_battery_level(self):
        return self._min_battery_level
    
    @property
    def export_threshold(self):
        return self._export_threshold
    
    @property
    def summer_temp(self):
        return self._summer_temp
    
    @property
    def winter_temp(self):
        return self._winter_temp
    
    @property
    def adaptive_offset(self):
        return self._adaptive_offset
    
    @property
    def boost_offset(self):
        return self._boost_offset

    async def async_setup(self):
        """Set up the manager."""
        self.entry.async_on_unload(self.entry.add_update_listener(self.async_update_options))
        
        track_entities: list[str] = []
        if self._grid_sensor:
            track_entities.append(self._grid_sensor)
        if self._battery_sensor:
            track_entities.append(self._battery_sensor)
        if self._ac_power_sensor:
            track_entities.append(self._ac_power_sensor)
        if self._heater_entity:
            track_entities.append(self._heater_entity)
        if self._ac_entity:
            track_entities.append(self._ac_entity)
        
        async_track_state_change_event(
            self.hass, track_entities, self._async_on_state_change
        )
        
        await self._async_check_conditions()

    def _read_current_humidity(self):
        humidity = None
        for entity_id in (self._heater_entity, self._ac_entity):
            if not entity_id:
                continue
            state = self.hass.states.get(entity_id)
            if not state:
                continue
            attrs = state.attributes
            value = attrs.get("current_humidity")
            if value is None:
                value = attrs.get("humidity")
            if value is None:
                continue
            try:
                humidity = float(value)
            except (TypeError, ValueError):
                continue
            else:
                break
        self._current_humidity = humidity
    
    def _read_current_temperatures(self):
        # Read AC Temperature
        if self._ac_entity:
            state = self.hass.states.get(self._ac_entity)
            if state:
                val = state.attributes.get("current_temperature")
                if val is not None:
                    try:
                        self._current_temp_ac = float(val)
                    except (TypeError, ValueError):
                        pass

        # Read Heater Temperature
        if self._heater_entity:
            state = self.hass.states.get(self._heater_entity)
            if state:
                val = state.attributes.get("current_temperature")
                if val is not None:
                    try:
                        self._current_temp_heater = float(val)
                    except (TypeError, ValueError):
                        pass

    @callback
    async def _async_on_state_change(self, event):
        """Handle state changes."""
        try:
            if event and self._ac_entity:
                ent = event.data.get("entity_id")
                if ent == self._ac_entity:
                    old_state = event.data.get("old_state")
                    new_state = event.data.get("new_state")
                    # If user (or any actor) turns AC off, start a 30-minute manual lock
                    if new_state and old_state and getattr(new_state, "state", None) == "off" and getattr(old_state, "state", None) != "off":
                        self._manual_lock_until = dt_util.utcnow() + timedelta(minutes=30)
        except Exception:
            pass
        await self._async_check_conditions()

    async def _async_check_conditions(self):
        """Check conditions and take action."""
        if not self._is_active:
            return

        self._read_current_humidity()
        self._read_current_temperatures()

        grid_state = self.hass.states.get(self._grid_sensor)
        battery_state = self.hass.states.get(self._battery_sensor) if self._battery_sensor else None
        ac_power_state = self.hass.states.get(self._ac_power_sensor) if self._ac_power_sensor else None

        if not grid_state:
            return

        try:
            raw_grid = float(grid_state.state)
            # Invert sign: User convention is Negative = Export.
            # We want Surplus to be Positive.
            # -4861 (Export) -> 4861 (Surplus)
            # +500 (Import) -> -500 (Deficit)
            grid_power = raw_grid * -1
            
            battery_level = None
            if battery_state and battery_state.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN):
                battery_level = float(battery_state.state)
            ac_power = None
            if ac_power_state and ac_power_state.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN):
                ac_power = float(ac_power_state.state)
        except ValueError:
            return

        self._current_surplus = grid_power
        self._battery_level = battery_level
        self._ac_power = ac_power
        
        if self._battery_sensor and battery_level is not None:
            if battery_level < self._min_battery_level:
                self._battery_low = True
                if self._is_boosting:
                    _LOGGER.info("Battery low (%s < %s), deactivating boost.", battery_level, self._min_battery_level)
                    self._is_boosting = False
                # Always ensure AC is off when battery is low
                await self._async_deactivate_boost()
                return
            self._battery_low = False
        else:
            self._battery_low = False

        # 2. Check surplus with simple hysteresis + min on/off
        now = dt_util.utcnow()
        min_on = timedelta(minutes=5)
        min_off = timedelta(minutes=2)
        eco_entry_delay = timedelta(minutes=5)
        eco_exit_delay = timedelta(minutes=2)
        
        # Respect manual lock: keep AC off and do not boost until lock expires
        if self._manual_lock_until is not None and now < self._manual_lock_until:
            if self._is_boosting:
                self._is_boosting = False
            await self._async_deactivate_boost()
            return
        
        if grid_power > self._export_threshold:
            # If we were in low surplus (Eco Mode candidate), we need to confirm the recovery
            if self._low_surplus_since is not None:
                # We do NOT reset _low_surplus_since immediately.
                # We need to see stable high power for 'eco_exit_delay'.
                pass
            
            if self._condition_met_since is None:
                self._condition_met_since = now
            
            # If condition met for more than 60 seconds (Activation) OR recovery from Eco
            elif (now - self._condition_met_since).total_seconds() > 60:
                
                # Check exit delay from Eco Mode
                if self._low_surplus_since is not None:
                    # We treat _condition_met_since as the start of "Recovery"
                    if (now - self._condition_met_since) > eco_exit_delay:
                         _LOGGER.info("Surplus recovered (>%s) for 2m. Exiting Eco Mode.", self._export_threshold)
                         self._low_surplus_since = None # Confirmed exit
                    else:
                         # Still waiting for stable sun to exit Eco
                         pass

                can_restart = (
                    self._last_boost_end is None
                    or (now - self._last_boost_end) >= min_off
                )
                if not self._is_boosting and can_restart:
                    _LOGGER.info("Export threshold met (%s > %s) for 60s, activating boost.", grid_power, self._export_threshold)
                    self._is_boosting = True
                    self._last_boost_start = now
                    await self._async_activate_boost()
                elif self._is_boosting:
                    # If already boosting, keep updating target temp (e.g. for adaptive logic)
                    await self._async_activate_boost()
        
        elif grid_power < 100:  # Turn off threshold (Surplus < 100W, i.e. starting to import)
            self._condition_met_since = None  # Reset activation timer
            if self._is_boosting:
                if self._last_boost_start is None or (now - self._last_boost_start) >= min_on:
                    # --- ECO MODE LOGIC ---
                    if self._low_surplus_since is None:
                         self._low_surplus_since = now
                         _LOGGER.debug("Surplus dropped below 100W (%s). Starting 5m timer for Eco Mode.", grid_power)
                    
                    # Calculate duration in low surplus
                    duration_low = now - self._low_surplus_since
                    
                    # 1. Check if we should ENTER Eco Mode (after 5 mins delay)
                    if duration_low > eco_entry_delay:
                        # We are effectively in Eco Mode range
                        
                        # 2. Check if we have exceeded the MAX Eco duration (60 mins) -> Turn OFF
                        if duration_low > timedelta(minutes=60):
                            _LOGGER.info("Export dropped below 100W (%s) for 60m, deactivating boost.", grid_power)
                            self._is_boosting = False
                            self._last_boost_end = now
                            self._low_surplus_since = None
                            await self._async_deactivate_boost()
                        else:
                            # Still in the 60m window: Modulate (Eco Mode)
                            await self._async_activate_boost()
                    else:
                         # Less than 5 mins of low surplus:
                         # Keep normal boosting (ignore short cloud)
                         _LOGGER.debug("Low surplus for %s (wait 5m for Eco). Maintaining Boost.", duration_low)
                         await self._async_activate_boost()

                else:
                    _LOGGER.debug("Export below 100W but min_on not reached, keeping boost active.")
        else:
            # Case: 100W <= grid_power <= export_threshold
            # We are in the safe zone (grey zone). Keep Eco timers running to allow 60m shutdown.
            self._condition_met_since = None
            if self._is_boosting:
                await self._async_activate_boost()

        is_winter = False
        if "Winter" in self._mode:
            is_winter = True
        elif self._mode == "Auto":
            current_month = dt_util.now().month
            is_winter = current_month >= 10 or current_month <= 4
            if self._outdoor_sensor:
                outdoor_state = self.hass.states.get(self._outdoor_sensor)
                if outdoor_state and outdoor_state.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN):
                    try:
                        out_temp = float(outdoor_state.state)
                        if out_temp < 20:
                            is_winter = True
                        else:
                            is_winter = False
                    except ValueError:
                        pass

        await self._async_sync_shared_group(is_winter)

    async def _async_activate_boost(self):
        """Activate cooling/heating."""
        self._is_dehumidifying = False
        self._is_eco_mode = False
        
        target_mode = "cool"
        target_temp = self._summer_temp
        is_winter = False
        
        # Adaptive Cooling Logic (Summer)
        if self._outdoor_sensor:
            outdoor_state = self.hass.states.get(self._outdoor_sensor)
            if outdoor_state:
                try:
                    outdoor_temp = float(outdoor_state.state)
                    calculated_target = outdoor_temp - self._adaptive_offset
                    
                    if calculated_target < self._summer_temp:
                         calculated_target = self._summer_temp
                    
                    if calculated_target > 28:
                        calculated_target = 28
                        
                    target_temp = round(calculated_target, 1)
                except ValueError:
                    pass

        if "Winter" in self._mode:
            is_winter = True
            target_mode = "heat"
            target_temp = self._winter_temp
            if self._heater_entity:
                state = self.hass.states.get(self._heater_entity)
                if state:
                    try:
                        setpoint = state.attributes.get("temperature")
                        if setpoint is not None:
                            setpoint = float(setpoint)
                            # Synergy: AC = Heater + Boost Offset
                            target_temp = setpoint + self._boost_offset
                    except ValueError:
                        pass
        elif self._mode == "Auto":
            current_month = dt_util.now().month
            is_winter = current_month >= 10 or current_month <= 4
            if self._outdoor_sensor:
                outdoor_state = self.hass.states.get(self._outdoor_sensor)
                if outdoor_state and outdoor_state.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN):
                    try:
                        out_temp = float(outdoor_state.state)
                        if out_temp < 20:
                            is_winter = True
                        else:
                            is_winter = False
                    except ValueError:
                        pass

            if is_winter:
                target_mode = "heat"
                target_temp = self._winter_temp
                if self._heater_entity:
                    state = self.hass.states.get(self._heater_entity)
                    if state:
                        try:
                            setpoint = state.attributes.get("temperature")
                            if setpoint is not None:
                                target_temp = float(setpoint) + self._boost_offset
                        except ValueError:
                            pass
            else:
                target_mode = "cool"

        # --- ECO MODE: If surplus < 100W for > 5 mins ---
        # Adjust setpoint to reduce load without turning off
        # NOTE: self._low_surplus_since is set when surplus < 100W.
        # But we only want to APPLY the Eco setpoint if the 5 mins have passed.
        
        apply_eco = False
        if self._low_surplus_since is not None:
             duration = dt_util.utcnow() - self._low_surplus_since
             if duration > timedelta(minutes=5):
                 apply_eco = True

        if apply_eco:
             # Force disable dehumidification to save power
             self._is_dehumidifying = False
             self._is_eco_mode = True
             
             # Dynamic Setpoint based on Ambient Temperature
             current_ambient_temp = None
             if self._ac_entity:
                 state = self.hass.states.get(self._ac_entity)
                 if state:
                     current_ambient_temp = state.attributes.get("current_temperature")
            
             if current_ambient_temp is not None:
                 try:
                     ambient = float(current_ambient_temp)
                     if target_mode == "cool":
                          # Summer: Setpoint = Ambient + 2°C (e.g. 25°C -> 27°C)
                          # This forces the compressor to minimum load or fan only
                          target_temp = ambient + 2.0
                          if target_temp > 30: target_temp = 30
                          if target_temp < 16: target_temp = 16
                     elif target_mode == "heat":
                          # Winter: Setpoint = Ambient - 2°C (e.g. 21°C -> 19°C)
                          # This reduces heating load significantly
                          target_temp = ambient - 2.0
                          if target_temp < 16: target_temp = 16
                          if target_temp > 30: target_temp = 30
                 except ValueError:
                     pass
             else:
                 # Fallback if current_temperature is not available: use previous fixed offset
                 if target_temp is not None:
                     try:
                         if target_mode == "cool":
                              target_temp = float(target_temp) + 2
                         elif target_mode == "heat":
                              target_temp = float(target_temp) - 2
                     except ValueError:
                         pass

        humidity = self._current_humidity
        if humidity is not None and self._humidity_threshold is not None:
            try:
                humidity_value = float(humidity)
                threshold = float(self._humidity_threshold)
            except (TypeError, ValueError):
                humidity_value = None
            if humidity_value is not None:
                hysteresis = 3.0
                if is_winter and not self._winter_dehum:
                    self._is_dehumidifying = False
                else:
                    if self._is_dehumidifying:
                        if humidity_value < threshold - hysteresis:
                            self._is_dehumidifying = False
                    else:
                        if humidity_value > threshold + hysteresis:
                            if self._low_surplus_since is None:
                                self._is_dehumidifying = True

        if self._is_dehumidifying and self._ac_entity:
            entity_id = self._ac_entity
            state = self.hass.states.get(entity_id)
            hvac_modes = state.attributes.get("hvac_modes") if state else None
            if is_winter and not self._winter_dehum:
                # Should not happen due to check above, but for safety:
                target_mode = "heat"
            else:
                if hvac_modes and "dry" in hvac_modes:
                    target_mode = "dry"
                else:
                    target_mode = "heat" if is_winter else "cool"
                
                # Logic for Dry Mode Temp:
                # If we are in Dry mode (or emulating it), we often want a specific temp behavior.
                # The +6 offset was likely intended to force the compressor on in heating mode to dry air?
                # BUT if we are in true 'dry' mode, the temp setting depends on the unit.
                # If we are in 'heat' mode (winter) but WANT to dehumidify (and winter_dehum is true),
                # maybe we wanted to overheat?
                
                # HOWEVER, the user is complaining about Heat Mode jumping to 27.5C when winter dehum is DISABLED.
                # If winter dehum is disabled, self._is_dehumidifying is set to False above.
                # So we should NOT be entering this block "if self._is_dehumidifying..." at all!
                
                if is_winter:
                    if target_temp is None:
                        target_temp = self._winter_temp
                    try:
                        # Only boost temp in winter if we are actively dehumidifying AND in heat mode
                        if target_mode == "heat":
                             target_temp = float(target_temp) + 6
                    except (TypeError, ValueError):
                        target_temp = self._winter_temp + 6
            
            # --- CORRECTION: Dehumidification in Winter (DRY Mode) ---
            # If we are in DRY mode in winter, we ALSO want a temperature boost (+6 or user defined)
            # to ensure the unit doesn't just circulate cold air.
            # Many ACs in DRY mode still look at the setpoint to decide if they should run the compressor.
            if is_winter and target_mode == "dry":
                 try:
                      if target_temp is None:
                          target_temp = self._winter_temp
                      target_temp = float(target_temp) + 6
                 except (TypeError, ValueError):
                      target_temp = self._winter_temp + 6
  
        # 1. Manage AC (Active Boost)
        # Use shared logic if applicable
        if self._shared_dehum:
             await self._async_sync_shared_group(is_winter)
             
             # Also ensure temperature is set correctly for this unit
             # (Sync handles Mode, but we handle Temp locally)
             if self._ac_entity:
                state = self.hass.states.get(self._ac_entity)
                if state:
                     current_temp = state.attributes.get("temperature")
                     
                     # Check if we should override temp due to shared mode VETO
                     # If the group was forced to HEAT due to Veto, we must ensure temp is reset to winter_temp
                     # and NOT keep the boosted temp from a previous dehumidification state.
                     if self._shared_dehum:
                         # Re-evaluate Veto logic locally to catch the temperature override
                         domain_managers = self.hass.data.get(DOMAIN, {})
                         winter_dehum_allowed = True
                         for _, m in domain_managers.items():
                            if getattr(m, "_shared_dehum", False) and getattr(m, "is_active", False):
                                if not getattr(m, "_winter_dehum", False):
                                    winter_dehum_allowed = False
                                    break
                         
                         # ECO PRIORITY: If we are in Eco Mode, do NOT reset the temperature to winter_temp.
                         # Keep the Eco setpoint (ambient - 2°C) to reduce power, while the group sync controls the HVAC mode.
                         if is_winter and not winter_dehum_allowed and not self._is_eco_mode and not self._is_boosting:
                             # VETO ACTIVE: Force standard winter temp
                             target_temp = self._winter_temp
                             # Also ensure we are not flagging as dehumidifying for UI
                             self._is_dehumidifying = False

                     if current_temp != target_temp:
                         await self.hass.services.async_call(
                             "climate",
                             "set_temperature",
                             {"entity_id": self._ac_entity, "temperature": target_temp},
                         )

        elif self._ac_entity:
            entity_id = self._ac_entity
            state = self.hass.states.get(entity_id)
            if state:
                # Set Mode if needed
                if state.state != target_mode:
                    await self.hass.services.async_call(
                        "climate",
                        "set_hvac_mode",
                        {"entity_id": entity_id, "hvac_mode": target_mode},
                    )

                # Set Temp if needed
                current_temp = state.attributes.get("temperature")
                if current_temp != target_temp:
                    await self.hass.services.async_call(
                        "climate",
                        "set_temperature",
                        {"entity_id": entity_id, "temperature": target_temp},
                    )

    async def _async_sync_shared_group(self, is_winter: bool):
        if not self._shared_dehum:
            return
        
        # Prevent recursion loop
        if self._is_syncing:
            return

        self._is_syncing = True
        try:
            domain_managers = self.hass.data.get(DOMAIN, {})
            group = []
            
            # 1. Identify the group and check Veto (Winter Dehumidification)
            winter_dehum_allowed = True
            for _, manager in domain_managers.items():
                try:
                    # Only include active managers with shared dehumidification enabled
                    if not getattr(manager, "_shared_dehum", False):
                        continue
                    if not getattr(manager, "is_active", False):
                        continue
                except Exception:
                    continue
                
                group.append(manager)
                
                # Check Veto: If ANY unit disables winter dehumidification, the whole group is blocked
                # We check this regardless of 'is_winter' to ensure the flag is correctly set
                if not getattr(manager, "_winter_dehum", False):
                    winter_dehum_allowed = False

            if not group:
                return

            # 2. Count Votes based on INTENT (is_dehumidifying flag), not current state
            # This prevents flip-flopping because the intent is stable based on humidity sensors
            votes_dry = 0
            votes_heat_cool = 0
            
            for manager in group:
                if getattr(manager, "_is_dehumidifying", False):
                    votes_dry += 1
                else:
                    votes_heat_cool += 1

            # 3. Determine Winner Mode
            target_mode_for_group = None
            
            if is_winter:
                # Winter Logic:
                # - If Veto is active (winter_dehum_allowed = False) -> Force HEAT
                # - If Dry votes > Heat votes -> DRY
                # - Otherwise -> HEAT
                if not winter_dehum_allowed:
                    target_mode_for_group = "heat"
                elif votes_dry > votes_heat_cool:
                    target_mode_for_group = "dry"
                else:
                    target_mode_for_group = "heat"
            else:
                # Summer Logic:
                # - If Dry votes > Cool votes -> DRY
                # - Otherwise -> COOL
                if votes_dry > votes_heat_cool:
                    target_mode_for_group = "dry"
                else:
                    target_mode_for_group = "cool"

            # 4. Apply Winner Mode to ALL group members
            for manager in group:
                ac_entity = getattr(manager, "_ac_entity", None)
                if not ac_entity:
                    continue
                
                state = self.hass.states.get(ac_entity)
                if not state:
                    continue
                
                # Skip if AC is off (user manually turned it off or boost inactive)
                # BUT if the manager is boosting, we MUST NOT skip it, otherwise it never turns on!
                if state.state == "off" and not getattr(manager, "is_boosting", False):
                    continue
                
                hvac_modes = state.attributes.get("hvac_modes")
                if not hvac_modes:
                    continue

                # Validate mode availability
                final_mode = target_mode_for_group
                if final_mode not in hvac_modes:
                    # Fallback if preferred mode is not available
                    if is_winter:
                        final_mode = "heat" if "heat" in hvac_modes else "off"
                    else:
                        final_mode = "cool" if "cool" in hvac_modes else "off"
                
                # Apply Mode
                if state.state != final_mode:
                    await self.hass.services.async_call(
                        "climate",
                        "set_hvac_mode",
                        {"entity_id": ac_entity, "hvac_mode": final_mode},
                    )

                # Apply Temperature (Each unit keeps its own target temp logic, 
                # but if we are forcing a mode change, we might need to refresh temp setting)
                # For now, we rely on the individual manager loop to set temp in the next cycle,
                # or we can set it here if critical. The main loop handles temp well.

        except Exception as e:
            _LOGGER.error("Error syncing group: %s", e)
        finally:
            self._is_syncing = False
          
    async def _async_deactivate_boost(self):
        """Deactivate boost."""
        if self._ac_entity:
             entity_id = self._ac_entity
             state = self.hass.states.get(entity_id)
             if state and state.state != "off":
                 await self.hass.services.async_call(
                    "climate", "set_hvac_mode",
                    {"entity_id": entity_id, "hvac_mode": "off"}
                 )

    @property
    def entry_id(self):
        """Return the entry_id."""
        return self.entry.entry_id

    @property
    def ac_entity(self):
        return self._ac_entity
        
    @property
    def heater_entity(self):
        return self._heater_entity

    @property
    def is_active(self):
        return self._is_active

    @property
    def is_boosting(self):
        return self._is_boosting
    
    @property
    def battery_low(self):
        return self._battery_low
        
    @property
    def battery_level(self):
        return self._battery_level
        
    @property
    def current_surplus(self):
        return self._current_surplus

    @property
    def ac_power(self):
        return self._ac_power

    @property
    def current_humidity(self):
        return self._current_humidity

    @property
    def humidity_threshold(self):
        return self._humidity_threshold

    @property
    def is_dehumidifying(self):
        return self._is_dehumidifying

    @property
    def is_eco_mode(self):
        return self._is_eco_mode

    @property
    def current_temp_ac(self):
        return self._current_temp_ac

    @property
    def current_temp_heater(self):
        return self._current_temp_heater

    @property
    def eco_since(self):
        if self._low_surplus_since is None:
            return None
        # Eco becomes active after 5 minutes from low_surplus_since
        eco_start = self._low_surplus_since + timedelta(minutes=5)
        if dt_util.utcnow() < eco_start:
            return None
        try:
            # Return ISO string for UI readability
            return eco_start.isoformat()
        except Exception:
            return None

    @property
    def eco_remaining_min(self):
        if self._low_surplus_since is None:
            return None
        now = dt_util.utcnow()
        eco_start = self._low_surplus_since + timedelta(minutes=5)
        if now < eco_start:
            return 60
        elapsed = now - eco_start
        remaining = 60 - int(elapsed.total_seconds() // 60)
        return max(0, remaining)

    @property
    def manual_lock_remaining_min(self):
        if self._manual_lock_until is None:
            return None
        now = dt_util.utcnow()
        if now >= self._manual_lock_until:
            return 0
        remaining = int((self._manual_lock_until - now).total_seconds() // 60)
        return max(0, remaining)

    @property
    def mode(self):
        return self._mode

    async def set_active(self, active: bool):
        self._is_active = active
        if not active:
            self._is_boosting = False
            self._condition_met_since = None
            self._last_boost_start = None
            self._low_surplus_since = None
        try:
            options = dict(self.entry.options)
        except Exception:
            options = {}
        options[CONF_AUTO_ACTIVE] = active
        self.hass.config_entries.async_update_entry(self.entry, options=options)

    async def set_mode(self, mode: str):
        self._mode = mode
        
    @staticmethod
    async def async_update_options(hass: HomeAssistant, entry: ConfigEntry):
        """Update options."""
        await hass.config_entries.async_reload(entry.entry_id)
