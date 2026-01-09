"""Constants for Disk Usage Breakdown."""
from __future__ import annotations

DOMAIN = "disk_usage_breakdown"
PLATFORMS = ["sensor"]

CONF_MOUNT_PATH = "mount_path"
CONF_INTERVAL = "scan_interval"
CONF_CATEGORIES = "categories"  # list of {"name": str, "path": str, "enabled": bool}

DEFAULT_MOUNT_PATH = "/"
DEFAULT_INTERVAL = 3600

DEFAULT_CATEGORIES = [
    {"name": "DB", "path": "/config/home-assistant_v2.db", "enabled": True},
    {"name": "Backups", "path": "/backup", "enabled": True},
    {"name": "Media", "path": "/media", "enabled": True},
    {"name": "Share", "path": "/share", "enabled": True},
    {"name": "Add-ons", "path": "/addons", "enabled": True},
]

SENSOR_PREFIX = "disk_usage"
