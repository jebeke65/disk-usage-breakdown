"""Update coordinator for Disk Usage Breakdown."""
from __future__ import annotations

import asyncio
import shutil
from dataclasses import dataclass
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


@dataclass(frozen=True)
class Category:
    name: str
    path: str


async def _run_du_bytes(path: str) -> int:
    """Return size in bytes for file/dir using du; returns 0 if path does not exist."""
    p = Path(path)
    if not p.exists():
        return 0

    candidates = [
        ("du", ["-sb", str(p)]),  # GNU coreutils
        ("du", ["-sk", str(p)]),  # KiB fallback
    ]

    for exe, args in candidates:
        try:
            proc = await asyncio.create_subprocess_exec(
                exe,
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
            )
            out, _ = await proc.communicate()
            if proc.returncode != 0 or not out:
                continue
            first = out.decode("utf-8", errors="ignore").strip().split()[0]
            val = int(first)
            if "-sk" in args:
                return val * 1024
            return val
        except FileNotFoundError:
            continue
        except Exception:
            continue

    # Fallback for files only
    try:
        if p.is_file():
            return p.stat().st_size
    except Exception:
        pass
    return 0


class DiskUsageCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator fetching sizes and computing 'Other'."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry

        self.mount_path: str = entry.data.get(CONF_MOUNT_PATH, DEFAULT_MOUNT_PATH)
        self.interval: int = entry.options.get(
            CONF_INTERVAL, entry.data.get(CONF_INTERVAL, DEFAULT_INTERVAL)
        )
        cat_cfg = entry.options.get(
            CONF_CATEGORIES, entry.data.get(CONF_CATEGORIES, DEFAULT_CATEGORIES)
        )

        self.categories: list[Category] = [
            Category(c["name"], c["path"])
            for c in cat_cfg
            if c.get("enabled", True) and c.get("name") and c.get("path")
        ]

        super().__init__(
            hass,
            logger=__import__("logging").getLogger(__name__),
            name="Disk Usage Breakdown",
            update_interval=timedelta(seconds=self.interval),
        )

    def _disk_usage(self) -> dict[str, int]:
        usage = shutil.disk_usage(self.mount_path)
        return {
            "total_bytes": int(usage.total),
            "used_bytes": int(usage.used),
            "free_bytes": int(usage.free),
        }

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            disk = await self.hass.async_add_executor_job(self._disk_usage)

            results = await asyncio.gather(*[_run_du_bytes(c.path) for c in self.categories])
            cat_sizes = {self.categories[i].name: int(results[i]) for i in range(len(self.categories))}

            known_sum = sum(cat_sizes.values())
            other = max(disk["used_bytes"] - known_sum, 0)

            return {
                "mount_path": self.mount_path,
                "disk": disk,
                "categories_bytes": cat_sizes,
                "other_bytes": int(other),
                "known_sum_bytes": int(known_sum),
            }
        except Exception as err:
            raise UpdateFailed(f"Failed to update disk usage: {err}") from err
