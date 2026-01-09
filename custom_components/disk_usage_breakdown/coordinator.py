from __future__ import annotations

import asyncio
import os
import math
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_INTERVAL,
    CONF_MAX_DEPTH,
    CONF_MIN_SIZE_MB,
    CONF_ROOTS,
    DEFAULT_INTERVAL,
    DEFAULT_MAX_DEPTH,
    DEFAULT_MIN_SIZE_MB,
    DEFAULT_ROOTS,
)

def _mb_ceil(b: int) -> int:
    return int(math.ceil(float(b) / 1024.0 / 1024.0))

async def du_tree_bytes(root: str, max_depth: int) -> dict[str, int]:
    """Return {path: bytes} for folders up to max_depth (inclusive) under root."""
    if not os.path.exists(root):
        return {}

    # -L follow symlinks, -x stay on same filesystem, -B1 bytes, -d depth
    proc = await asyncio.create_subprocess_exec(
        "du",
        "-LxB1",
        f"-d{max_depth}",
        root,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL,
    )
    out, _ = await proc.communicate()
    if proc.returncode != 0:
        return {}

    result: dict[str, int] = {}
    for line in out.decode("utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            size_s, path = line.split("\t", 1)
            result[path] = int(size_s)
        except Exception:
            continue
    return result

class DiskUsageCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        opts = entry.options or {}
        data = entry.data or {}

        self.interval: int = opts.get(CONF_INTERVAL, data.get(CONF_INTERVAL, DEFAULT_INTERVAL))
        self.roots: list[str] = opts.get(CONF_ROOTS, data.get(CONF_ROOTS, DEFAULT_ROOTS))
        self.max_depth: int = int(opts.get(CONF_MAX_DEPTH, data.get(CONF_MAX_DEPTH, DEFAULT_MAX_DEPTH)))
        self.min_size_mb: int = int(opts.get(CONF_MIN_SIZE_MB, data.get(CONF_MIN_SIZE_MB, DEFAULT_MIN_SIZE_MB)))

        super().__init__(
            hass,
            __import__("logging").getLogger(__name__),
            name="Disk Usage Breakdown",
            update_interval=timedelta(seconds=self.interval),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            roots_data: dict[str, dict[str, int]] = {}
            all_paths: dict[str, int] = {}

            for r in self.roots:
                tree = await du_tree_bytes(r, self.max_depth)
                # filter noise by min size MB
                tree = {p: b for p, b in tree.items() if _mb_ceil(b) >= self.min_size_mb}
                roots_data[r] = tree
                all_paths.update(tree)

            return {
                "roots": list(self.roots),
                "paths": all_paths,      # {path: bytes}
                "per_root": roots_data,  # {root: {path: bytes}}
                "max_depth": self.max_depth,
                "min_size_mb": self.min_size_mb,
            }
        except Exception as err:
            raise UpdateFailed(f"Disk usage update failed: {err}") from err
