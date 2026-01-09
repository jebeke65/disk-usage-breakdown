from __future__ import annotations

import hashlib
import math
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN
from .coordinator import DiskUsageCoordinator

def mb_ceil(bytes_val: int) -> int:
    return int(math.ceil(float(bytes_val) / 1024.0 / 1024.0))

def uid_for(entry_id: str, path: str) -> str:
    h = hashlib.sha1(path.encode("utf-8")).hexdigest()[:12]
    return f"{entry_id}_{h}"

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coord: DiskUsageCoordinator = hass.data[DOMAIN][entry.entry_id]
    ent_reg = er.async_get(hass)

    entities: dict[str, PathSizeSensor] = {}

    def desired_paths() -> set[str]:
        data = coord.data or {}
        return set((data.get("paths") or {}).keys())

    async def add_new(new_paths: set[str]) -> None:
        new_entities = []
        for p in sorted(new_paths):
            if p in entities:
                continue
            e = PathSizeSensor(coord, entry, p)
            entities[p] = e
            new_entities.append(e)
        if new_entities:
            async_add_entities(new_entities)

    async def remove_old(removed_paths: set[str]) -> None:
        for p in removed_paths:
            e = entities.pop(p, None)
            if e is None:
                continue
            # Remove from entity registry (so it disappears for the user)
            if e.entity_id:
                ent_reg.async_remove(e.entity_id)
            await e.async_remove(force_remove=True)

    @callback
    def _handle_update() -> None:
        want = desired_paths()
        have = set(entities.keys())
        to_add = want - have
        to_remove = have - want

        if to_add:
            hass.async_create_task(add_new(to_add))
        if to_remove:
            hass.async_create_task(remove_old(to_remove))

    await add_new(desired_paths())
    coord.async_add_listener(_handle_update)

class PathSizeSensor(CoordinatorEntity[DiskUsageCoordinator], SensorEntity):
    _attr_native_unit_of_measurement = "MB"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:folder"

    def __init__(self, coordinator: DiskUsageCoordinator, entry: ConfigEntry, path: str) -> None:
        super().__init__(coordinator)
        self._path = path
        self._attr_name = path
        self._attr_unique_id = uid_for(entry.entry_id, path)

    @property
    def native_value(self) -> int:
        data = self.coordinator.data or {}
        b = int((data.get("paths") or {}).get(self._path, 0))
        return mb_ceil(b)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        return {"path": self._path, "max_depth": data.get("max_depth"), "min_size_mb": data.get("min_size_mb")}
