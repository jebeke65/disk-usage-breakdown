DOMAIN = "disk_usage_breakdown"
PLATFORMS = ["sensor"]

CONF_MOUNT_PATH = "mount_path"
CONF_INTERVAL = "scan_interval"
CONF_CATEGORIES = "categories"

DEFAULT_MOUNT_PATH = "/mnt/data"
DEFAULT_INTERVAL = 3600

DEFAULT_CATEGORIES = [
    {"name": "Docker", "path": "/mnt/data/docker", "enabled": True},
    {"name": "Supervisor", "path": "/mnt/data/supervisor", "enabled": True},
    {"name": "Home Assistant", "path": "/mnt/data/supervisor/homeassistant", "enabled": True},
    {"name": "Share", "path": "/mnt/data/supervisor/share", "enabled": True},
    {"name": "Media", "path": "/mnt/data/supervisor/media", "enabled": True},
    {"name": "Backup", "path": "/mnt/data/supervisor/backup", "enabled": True},
    {"name": "Journal", "path": "/var/log/journal", "enabled": True},
]
