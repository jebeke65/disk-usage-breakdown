import math
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

def mb_ceil(b):
    return int(math.ceil(b / 1024 / 1024))

async def async_setup_entry(hass, entry, async_add_entities):
    coord = hass.data[DOMAIN][entry.entry_id]
    entities = []

    for name in coord.categories:
        if name.get('enabled', True):
            entities.append(CategorySensor(coord, name['name']))

    entities.append(OtherSensor(coord))
    entities.append(SystemSensor(coord))

    async_add_entities(entities)

class Base(CoordinatorEntity, SensorEntity):
    _attr_unit_of_measurement = 'MB'
    _attr_icon = 'mdi:harddisk'

class CategorySensor(Base):
    def __init__(self, coord, name):
        super().__init__(coord)
        self._name = name
        self._attr_name = f'Disk usage {name}'
        self._attr_unique_id = f"{coord.config_entry.entry_id}_{name.lower().replace(' ','_')}_mb"

    @property
    def native_value(self):
        return mb_ceil(self.coordinator.data['sizes'].get(self._name, 0))

class OtherSensor(Base):
    _attr_name = 'Disk usage Other'
    _attr_unique_id = 'disk_usage_other_mb'
    @property
    def native_value(self):
        return mb_ceil(self.coordinator.data['other'])

class SystemSensor(Base):
    _attr_name = 'Disk usage System'
    _attr_unique_id = 'disk_usage_system_mb'
    @property
    def native_value(self):
        return mb_ceil(self.coordinator.data['system'])
