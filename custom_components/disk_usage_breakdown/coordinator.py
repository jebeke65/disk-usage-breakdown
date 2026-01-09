from __future__ import annotations

import asyncio
import shutil
from datetime import timedelta
from pathlib import Path
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_CATEGORIES,
    CONF_INTERVAL,
    CONF_MOUNT_PATH,
    DEFAULT_CATEGORIES,
    DEFAULT_INTERVAL,
    DEFAULT_MOUNT_PATH,
)

async def du_bytes(path: str) -> int:
    p = Path(path)
    if not p.exists():
        return 0

    # Prefer bytes; fall back to KiB.
    for args, mul in ((["-sb"], 1), (["-sk"], 1024)):
        try:
            proc = await asyncio.create_subprocess_exec(
                "du",
                *args,
                str(p),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
            )
            out, _ = await proc.communicate()
            if proc.returncode == 0 and out:
                return int(out.split()[0]) * mul
        except Exception:
            continue

    return 0

class DiskUsageCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        self.mount: str = entry.data.get(CONF_MOUNT_PATH, DEFAULT_MOUNT_PATH)
        self.interval: int = entry.options.get(CONF_INTERVAL, entry.data.get(CONF_INTERVAL, DEFAULT_INTERVAL))
        self.categories: list[dict[str, Any]] = entry.options.get(CONF_CATEGORIES, entry.data.get(CONF_CATEGORIES, DEFAULT_CATEGORIES))

        super().__init__(
            hass,
            __import__("logging").getLogger(__name__),
            name="Disk Usage Breakdown",
            update_interval=timedelta(seconds=self.interval),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            disk = shutil.disk_usage(self.mount)

            sizes: dict[str, int] = {}
            for c in self.categories:
                if c.get("enabled", True) and c.get("name") and c.get("path"):
                    sizes[c["name"]] = await du_bytes(c["path"])

            known = sum(sizes.values())
            other = max(int(disk.used) - int(known), 0)

            user_keys = {"Home Assistant", "Share", "Media", "Backup"}
            user_sum = sum(v for k, v in sizes.items() if k in user_keys)
            system = max(int(disk.used) - int(user_sum), 0)

            return {
                "mount": self.mount,
                "disk_used": int(disk.used),
                "sizes": sizes,
                "other": int(other),
                "system": int(system),
            }
        except Exception as err:
            raise UpdateFailed(f"Disk usage update failed: {err}") from err
