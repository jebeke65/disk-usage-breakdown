DOMAIN = "disk_usage_breakdown"
PLATFORMS = ["sensor"]

CONF_ROOTS = "roots"
CONF_INTERVAL = "scan_interval"
CONF_MAX_DEPTH = "max_depth"
CONF_MIN_SIZE_MB = "min_size_mb"

DEFAULT_INTERVAL = 3600
DEFAULT_ROOTS = ["/config", "/media", "/share", "/backup"]
DEFAULT_MAX_DEPTH = 2
DEFAULT_MIN_SIZE_MB = 1
