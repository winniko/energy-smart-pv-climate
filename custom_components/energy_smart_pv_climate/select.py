from homeassistant.components.select import SelectEntity
from .const import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add select for passed config_entry in HA."""
    manager = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities([EnergySmartPVModeSelect(manager)])

class EnergySmartPVModeSelect(SelectEntity):
    """Representation of the mode selector."""

    def __init__(self, manager):
        self._manager = manager
        self._attr_name = f"{manager.entry.title} Mode"
        self._attr_unique_id = f"{manager.entry_id}_mode"
        self._attr_options = ["Summer (Cooling)", "Winter (Heating)", "Auto"]
        self._attr_current_option = manager.mode

    @property
    def device_info(self):
        """Return device information about this entity."""
        return {
            "identifiers": {(DOMAIN, self._manager.entry_id)},
            "name": f"Energy Smart PV - {self._manager.entry.title}",
            "manufacturer": "Custom Component",
            "model": "Energy Smart PV",
        }

    @property
    def current_option(self):
        """Return the current selected option."""
        return self._manager.mode

    async def async_added_to_hass(self):
        """Run when entity about to be added to hass."""
        self._manager.set_select_entity(self.entity_id)

    async def async_select_option(self, option: str):
        """Change the selected option."""
        await self._manager.set_mode(option)
        self._attr_current_option = option
