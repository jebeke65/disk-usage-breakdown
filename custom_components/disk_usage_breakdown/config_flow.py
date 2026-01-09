import voluptuous as vol
from homeassistant import config_entries
from .const import *

class DiskUsageConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        if user_input:
            return self.async_create_entry(
                title='Disk Usage (/mnt/data)',
                data={CONF_MOUNT_PATH: user_input[CONF_MOUNT_PATH]},
            )
        return self.async_show_form(
            step_id='user',
            data_schema=vol.Schema({
                vol.Optional(CONF_MOUNT_PATH, default=DEFAULT_MOUNT_PATH): str,
            })
        )
