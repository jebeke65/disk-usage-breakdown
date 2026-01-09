"""Sensors for Disk Usage Breakdown."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import DiskUsageCoordinator


def _slug(name: str) -> str:
    return (
        name.strip()
        .lower()
        .replace("&", "and")
        .replace("/", "_")
        .replace(" ", "_")
        .replace("-", "_")
    )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator: DiskUsageCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[SensorEntity] = []

    entities.append(DiskBytesToMbSensor(coordinator, entry, "total", "Total", "disk.total_bytes"))
    entities.append(DiskBytesToMbSensor(coordinator, entry, "used", "Used", "disk.used_bytes"))
    entities.append(DiskBytesToMbSensor(coordinator, entry, "free", "Free", "disk.free_bytes"))

    for cat in coordinator.categories:
        entities.append(CategoryBytesToMbSensor(coordinator, entry, cat.name, cat.path))

    entities.append(OtherBytesToMbSensor(coordinator, entry))

    async_add_entities(entities)


class BaseMbSensor(CoordinatorEntity[DiskUsageCoordinator], SensorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "MB"
    _attr_icon = "mdi:harddisk"

    def __init__(self, coordinator: DiskUsageCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry

    @property
    def available(self) -> bool:
        return super().available and self.coordinator.data is not None


class DiskBytesToMbSensor(BaseMbSensor):
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: DiskUsageCoordinator, entry: ConfigEntry, key: str, label: str, data_path: str) -> None:
        super().__init__(coordinator, entry)
        self._key = key
        self._label = label
        self._data_path = data_path
        self._attr_unique_id = f"{entry.entry_id}_disk_{key}_mb"
        self._attr_name = f"Disk Usage {label} (MB)"

    @property
    def native_value(self) -> float:
        data = self.coordinator.data or {}
        cur: Any = data
        for part in self._data_path.split("."):
            cur = cur.get(part, 0) if isinstance(cur, dict) else 0
        return round(float(cur) / (1024 * 1024), 0)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {"mount_path": self.coordinator.mount_path}


class CategoryBytesToMbSensor(BaseMbSensor):
    def __init__(self, coordinator: DiskUsageCoordinator, entry: ConfigEntry, name: str, path: str) -> None:
        super().__init__(coordinator, entry)
        self._cat_name = name
        self._path = path
        slug = _slug(name)
        self._attr_unique_id = f"{entry.entry_id}_cat_{slug}_mb"
        self._attr_name = f"Disk Usage {name} (MB)"

    @property
    def native_value(self) -> float:
        data = self.coordinator.data or {}
        b = (data.get("categories_bytes") or {}).get(self._cat_name, 0)
        return round(float(b) / (1024 * 1024), 0)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {"path": self._path, "mount_path": self.coordinator.mount_path}


class OtherBytesToMbSensor(BaseMbSensor):
    def __init__(self, coordinator: DiskUsageCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_other_mb"
        self._attr_name = "Disk Usage Other (MB)"

    @property
    def native_value(self) -> float:
        data = self.coordinator.data or {}
        b = data.get("other_bytes", 0)
        return round(float(b) / (1024 * 1024), 0)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        return {
            "mount_path": self.coordinator.mount_path,
            "known_sum_mb": round(float(data.get("known_sum_bytes", 0)) / (1024 * 1024), 0),
        }
