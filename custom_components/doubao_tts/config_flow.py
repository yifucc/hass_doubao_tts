from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
)
from .const import (
    DOMAIN, 
    DEFAULT_TITLE, 
    DEFAULT_VOICE,
    DEFAULT_SPEED,
    DEFAULT_VOLUME,
    CONF_APP_ID,
    CONF_ACCESS_KEY,
    CONF_VOICE, 
    CONF_SPEED, 
    CONF_VOLUME,
    SPEED_MIN,
    SPEED_MAX,
    SPEED_STEP,
    VOLUME_MIN,
    VOLUME_MAX,
    VOLUME_STEP,
)
from .voice_const import SUPPORTED_VOICES

class DoubaoTTSConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title=DEFAULT_TITLE, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_APP_ID): str,
                vol.Required(CONF_ACCESS_KEY): str,
            })
        )

    def async_get_options_flow(config_entry):
        return DoubaoTTSOptionsFlowHandler(config_entry)


class DoubaoTTSOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title=DEFAULT_TITLE, data=user_input)
        
        options = self._config_entry.options

        voice_options = [{"value": voice_id, "label": voice_info["name"]} for voice_id, voice_info in SUPPORTED_VOICES.items()]

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    CONF_VOICE,
                    default=options.get(CONF_VOICE, DEFAULT_VOICE),
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=voice_options,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(
                    CONF_SPEED,
                    default=options.get(CONF_SPEED, DEFAULT_SPEED),
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=SPEED_MIN, max=SPEED_MAX,
                        step=SPEED_STEP, mode=NumberSelectorMode.SLIDER
                    )
                ),
                vol.Optional(
                    CONF_VOLUME,
                    default=options.get(CONF_VOLUME, DEFAULT_VOLUME),
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=VOLUME_MIN, max=VOLUME_MAX,
                        step=VOLUME_STEP, mode=NumberSelectorMode.SLIDER
                    )
                ),
            })
        )
