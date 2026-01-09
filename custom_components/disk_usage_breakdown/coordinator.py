import asyncio, shutil, math
from datetime import timedelta
from pathlib import Path
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import *

async def du_bytes(path: str) -> int:
    p = Path(path)
    if not p.exists():
        return 0
    for args, mul in [(['-sb'],1), (['-sk'],1024)]:
        try:
            proc = await asyncio.create_subprocess_exec(
                'du', *args, str(p),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
            )
            out,_ = await proc.communicate()
            if out:
                return int(out.split()[0]) * mul
        except Exception:
            pass
    return 0

class DiskUsageCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry):
        self.mount = entry.data.get(CONF_MOUNT_PATH, DEFAULT_MOUNT_PATH)
        self.interval = entry.options.get(CONF_INTERVAL, DEFAULT_INTERVAL)
        self.categories = entry.options.get(CONF_CATEGORIES, DEFAULT_CATEGORIES)
        super().__init__(hass, __import__('logging').getLogger(__name__),
            'Disk Usage Breakdown', timedelta(seconds=self.interval))

    async def _async_update_data(self):
        try:
            disk = shutil.disk_usage(self.mount)
            sizes = {}
            for c in self.categories:
                if c.get('enabled', True):
                    sizes[c['name']] = await du_bytes(c['path'])
            known = sum(sizes.values())
            other = max(disk.used - known, 0)

            user_keys = {'Home Assistant','Share','Media','Backup'}
            user_sum = sum(v for k,v in sizes.items() if k in user_keys)
            system = max(disk.used - user_sum, 0)

            return {'sizes': sizes, 'other': other, 'system': system}
        except Exception as e:
            raise UpdateFailed(e)
