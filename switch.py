from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add switch for passed config_entry in HA."""
    manager = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities([EnergySmartPVSwitch(manager)])

class EnergySmartPVSwitch(SwitchEntity):
    """Representation of a Energy Smart PV Switch."""

    def __init__(self, manager):
        self._manager = manager
        self._attr_name = f"{manager.entry.title} Auto Mode"
        self._attr_unique_id = f"{manager.entry_id}_auto_mode"
        self._attr_is_on = True  # Default to on

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
    def is_on(self):
        """Return true if switch is on."""
        return self._manager.is_active

    async def async_added_to_hass(self):
        """Run when entity about to be added to hass."""
        self._manager.set_switch_entity(self.entity_id)
        
    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        await self._manager.set_active(True)
        self._attr_is_on = True

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        await self._manager.set_active(False)
        self._attr_is_on = False
