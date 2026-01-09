from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN, CONF_MOUNT_PATH, DEFAULT_MOUNT_PATH

class DiskUsageConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            mount = user_input[CONF_MOUNT_PATH]
            return self.async_create_entry(
                title=f"Disk Usage ({mount})",
                data={CONF_MOUNT_PATH: mount},
            )

        schema = vol.Schema({
            vol.Optional(CONF_MOUNT_PATH, default=DEFAULT_MOUNT_PATH): str,
        })
        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return DiskUsageOptionsFlow(config_entry)

class DiskUsageOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        # Keep it minimal in v0.2.1 (no category editing here yet) – avoids breaking changes.
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({}),
            description_placeholders={},
        )
