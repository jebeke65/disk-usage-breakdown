from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    DOMAIN,
    CONF_INTERVAL,
    CONF_ROOTS,
    CONF_MAX_DEPTH,
    CONF_MIN_SIZE_MB,
    DEFAULT_INTERVAL,
    DEFAULT_ROOTS,
    DEFAULT_MAX_DEPTH,
    DEFAULT_MIN_SIZE_MB,
)

class DiskUsageConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title="Disk Usage Breakdown",
                data={
                    CONF_ROOTS: user_input[CONF_ROOTS],
                    CONF_MAX_DEPTH: user_input[CONF_MAX_DEPTH],
                    CONF_MIN_SIZE_MB: user_input[CONF_MIN_SIZE_MB],
                    CONF_INTERVAL: user_input[CONF_INTERVAL],
                },
            )

        schema = vol.Schema({
            vol.Optional(CONF_ROOTS, default=DEFAULT_ROOTS): [str],
            vol.Optional(CONF_MAX_DEPTH, default=DEFAULT_MAX_DEPTH): int,
            vol.Optional(CONF_MIN_SIZE_MB, default=DEFAULT_MIN_SIZE_MB): int,
            vol.Optional(CONF_INTERVAL, default=DEFAULT_INTERVAL): int,
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
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema({
            vol.Optional(CONF_ROOTS, default=self.config_entry.options.get(CONF_ROOTS, self.config_entry.data.get(CONF_ROOTS, DEFAULT_ROOTS))): [str],
            vol.Optional(CONF_MAX_DEPTH, default=self.config_entry.options.get(CONF_MAX_DEPTH, self.config_entry.data.get(CONF_MAX_DEPTH, DEFAULT_MAX_DEPTH))): int,
            vol.Optional(CONF_MIN_SIZE_MB, default=self.config_entry.options.get(CONF_MIN_SIZE_MB, self.config_entry.data.get(CONF_MIN_SIZE_MB, DEFAULT_MIN_SIZE_MB))): int,
            vol.Optional(CONF_INTERVAL, default=self.config_entry.options.get(CONF_INTERVAL, self.config_entry.data.get(CONF_INTERVAL, DEFAULT_INTERVAL))): int,
        })
        return self.async_show_form(step_id="init", data_schema=schema)
