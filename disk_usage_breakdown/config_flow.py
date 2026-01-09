"""Config flow for Disk Usage Breakdown."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    DOMAIN,
    CONF_MOUNT_PATH,
    CONF_INTERVAL,
    CONF_CATEGORIES,
    DEFAULT_MOUNT_PATH,
    DEFAULT_INTERVAL,
    DEFAULT_CATEGORIES,
)


def _cats_to_form(cats: list[dict]) -> vol.Schema:
    schema: dict = {}
    for idx, c in enumerate(cats):
        prefix = f"cat_{idx}_"
        schema[vol.Optional(prefix + "enabled", default=c.get("enabled", True))] = bool
        schema[vol.Optional(prefix + "name", default=c.get("name", ""))] = str
        schema[vol.Optional(prefix + "path", default=c.get("path", ""))] = str
    return vol.Schema(schema)


def _form_to_cats(user_input: dict, count: int) -> list[dict]:
    cats: list[dict] = []
    for idx in range(count):
        prefix = f"cat_{idx}_"
        cats.append(
            {
                "enabled": bool(user_input.get(prefix + "enabled", True)),
                "name": str(user_input.get(prefix + "name", "")).strip(),
                "path": str(user_input.get(prefix + "path", "")).strip(),
            }
        )
    return cats


class DiskUsageConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title=f"Disk Usage ({user_input[CONF_MOUNT_PATH]})",
                data={
                    CONF_MOUNT_PATH: user_input[CONF_MOUNT_PATH],
                    CONF_INTERVAL: int(user_input[CONF_INTERVAL]),
                    CONF_CATEGORIES: DEFAULT_CATEGORIES,
                },
            )

        schema = vol.Schema(
            {
                vol.Optional(CONF_MOUNT_PATH, default=DEFAULT_MOUNT_PATH): str,
                vol.Optional(CONF_INTERVAL, default=DEFAULT_INTERVAL): vol.Coerce(int),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return DiskUsageOptionsFlow(config_entry)


class DiskUsageOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry
        self._cats = list(
            config_entry.options.get(
                CONF_CATEGORIES,
                config_entry.data.get(CONF_CATEGORIES, DEFAULT_CATEGORIES),
            )
        )
        self._count = max(len(self._cats), 8)
        while len(self._cats) < self._count:
            self._cats.append({"enabled": False, "name": "", "path": ""})

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            opts = {
                CONF_INTERVAL: int(user_input.get(CONF_INTERVAL, DEFAULT_INTERVAL)),
                CONF_CATEGORIES: _form_to_cats(user_input, self._count),
            }
            return self.async_create_entry(title="", data=opts)

        schema_dict = {
            vol.Optional(
                CONF_INTERVAL,
                default=self.config_entry.options.get(
                    CONF_INTERVAL,
                    self.config_entry.data.get(CONF_INTERVAL, DEFAULT_INTERVAL),
                ),
            ): vol.Coerce(int),
        }
        schema_dict.update(_cats_to_form(self._cats).schema)
        return self.async_show_form(step_id="init", data_schema=vol.Schema(schema_dict))
