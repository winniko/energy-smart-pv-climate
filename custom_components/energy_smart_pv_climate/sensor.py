from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.const import UnitOfPower
from .const import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add sensors for passed config_entry in HA."""
    manager = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities([
        EnergySmartPVStatusSensor(manager),
        EnergySmartPVSurplusSensor(manager)
    ])

class EnergySmartPVStatusSensor(SensorEntity):
    """Representation of the system status."""

    def __init__(self, manager):
        self._manager = manager
        # Use the config entry title to create a unique friendly name
        self._attr_name = f"{manager.entry.title} Status"
        self._attr_unique_id = f"{manager.entry_id}_status"

    @property
    def device_info(self):
        """Return device information about this entity."""
        return {
            "identifiers": {(DOMAIN, self._manager.entry_id)},
            "name": f"Energy Smart PV Climate - {self._manager.entry.title}",
            "manufacturer": "Custom Component",
            "model": "Energy Smart PV Climate",
        }

    @property
    def state(self):
        """Return the state of the sensor."""
        if not self._manager.is_active:
            return "Disabled"
        if self._manager.is_boosting:
            return "Boosting (Using Excess)"
        if self._manager.battery_low:
            return "Charging Battery"
        return "Idle (Monitoring)"

    @property
    def icon(self):
        """Return the icon of the sensor."""
        if self._manager.is_boosting:
            return "mdi:flash"
        return "mdi:solar-power"

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "ac_entity": self._manager.ac_entity,
            "heater_entity": self._manager.heater_entity,
            "surplus_power": self._manager.current_surplus,
            "battery_level": self._manager.battery_level,
            "ac_power": self._manager.ac_power,
            "min_battery_level": self._manager.min_battery_level,
            "export_threshold": self._manager.export_threshold,
            "summer_temp": self._manager.summer_temp,
            "winter_temp": self._manager.winter_temp,
            "adaptive_offset": self._manager.adaptive_offset,
            "boost_offset": self._manager.boost_offset,
            "mode": self._manager.mode,
            "is_active": self._manager.is_active,
            "switch_entity": self._manager.switch_entity_id,
            "select_entity": self._manager.select_entity_id,
            "entry_id": self._manager.entry_id,
            "current_humidity": self._manager.current_humidity,
            "humidity_threshold": self._manager.humidity_threshold,
            "is_dehumidifying": self._manager.is_dehumidifying,
            "outdoor_sensor": self._manager.outdoor_sensor,
            "outdoor_humidity_sensor": self._manager.outdoor_humidity_sensor,
            "shared_dehumidification": getattr(self._manager, "_shared_dehum", False),
            "winter_dehumidification": getattr(self._manager, "_winter_dehum", False),
            "is_eco_mode": self._manager.is_eco_mode,
            "current_temp_ac": self._manager.current_temp_ac,
            "current_temp_heater": self._manager.current_temp_heater,
            "eco_since": self._manager.eco_since,
            "eco_remaining_min": self._manager.eco_remaining_min,
            "manual_lock_remaining_min": self._manager.manual_lock_remaining_min,
            "eco_offset": 2,
        }

class EnergySmartPVSurplusSensor(SensorEntity):
    """Representation of the calculated surplus power."""

    def __init__(self, manager):
        self._manager = manager
        self._attr_name = f"{manager.entry.title} Surplus Power"
        self._attr_unique_id = f"{manager.entry_id}_surplus_power"
        self._attr_native_unit_of_measurement = UnitOfPower.WATT
        self._attr_device_class = SensorDeviceClass.POWER

    @property
    def device_info(self):
        """Return device information about this entity."""
        return {
            "identifiers": {(DOMAIN, self._manager.entry_id)},
            "name": f"Energy Smart PV Climate - {self._manager.entry.title}",
            "manufacturer": "Custom Component",
            "model": "Energy Smart PV Climate",
        }

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._manager.current_surplus
