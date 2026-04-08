"""Config flow for Doubao TTS."""
import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN

class DoubaoTTSConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Doubao TTS", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("app_id"): str,
                vol.Required("access_key"): str,
                vol.Required("resource_id", default="seed-tts-2.0"): str,
            })
        )