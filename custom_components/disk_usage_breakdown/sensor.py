
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import EntityCategory


def slugify(value: str) -> str:
    return (
        value.strip()
        .lower()
        .replace("&", "and")
        .replace("/", "_")
        .replace(" ", "_")
        .replace("-", "_")
    )


class PathSizeSensor(SensorEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = "MB"
    _attr_icon = "mdi:harddisk"

    def __init__(self, *, name: str, unique_id: str):
        slug = slugify(name)

        self._attr_name = name
        self._attr_unique_id = unique_id

        # Force entity_id prefix
        self._attr_suggested_object_id = f"disk_usage_{slug}_mb"

        self._state: float | None = None

    @property
    def native_value(self):
        return self._state

    def set_state(self, mb: float):
        self._state = round(mb, 0)
