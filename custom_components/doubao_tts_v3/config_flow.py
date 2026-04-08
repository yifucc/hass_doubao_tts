from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

from .const import DOMAIN, RESOURCE_ID

class DoubaoTTSV3ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title="豆包TTS V3 流式",
                data=user_input
            )

        schema = vol.Schema({
            vol.Required("app_id"): str,
            vol.Required("access_key"): str,
            vol.Optional("resource_id", default=RESOURCE_ID): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema
        )