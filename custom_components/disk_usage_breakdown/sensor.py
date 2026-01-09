from __future__ import annotations

import math
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import DiskUsageCoordinator

def mb_ceil(bytes_val: int) -> int:
    return int(math.ceil(float(bytes_val) / 1024.0 / 1024.0))

def slug(name: str) -> str:
    return (
        name.strip()
        .lower()
        .replace("&", "and")
        .replace("/", "_")
        .replace("-", "_")
        .replace(" ", "_")
    )

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coord: DiskUsageCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[SensorEntity] = []

    for c in coord.categories:
        if c.get("enabled", True) and c.get("name"):
            entities.append(CategorySensor(coord, entry, c["name"], c.get("path", "")))

    entities.append(OtherSensor(coord, entry))
    entities.append(SystemSensor(coord, entry))

    async_add_entities(entities)

class Base(CoordinatorEntity[DiskUsageCoordinator], SensorEntity):
    _attr_native_unit_of_measurement = "MB"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:harddisk"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: DiskUsageCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        return {"mount_path": data.get("mount")}

class CategorySensor(Base):
    def __init__(self, coordinator: DiskUsageCoordinator, entry: ConfigEntry, name: str, path: str) -> None:
        super().__init__(coordinator, entry)
        self._cat_name = name
        self._path = path
        self._attr_name = f"Disk usage {name}"
        self._attr_unique_id = f"{entry.entry_id}_cat_{slug(name)}_mb"

    @property
    def native_value(self) -> int:
        data = self.coordinator.data or {}
        b = (data.get("sizes") or {}).get(self._cat_name, 0)
        return mb_ceil(int(b))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        attrs = super().extra_state_attributes
        attrs.update({"path": self._path})
        return attrs

class OtherSensor(Base):
    def __init__(self, coordinator: DiskUsageCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_name = "Disk usage Other"
        self._attr_unique_id = f"{entry.entry_id}_other_mb"

    @property
    def native_value(self) -> int:
        data = self.coordinator.data or {}
        return mb_ceil(int(data.get("other", 0)))

class SystemSensor(Base):
    def __init__(self, coordinator: DiskUsageCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_name = "Disk usage System"
        self._attr_unique_id = f"{entry.entry_id}_system_mb"

    @property
    def native_value(self) -> int:
        data = self.coordinator.data or {}
        return mb_ceil(int(data.get("system", 0)))
