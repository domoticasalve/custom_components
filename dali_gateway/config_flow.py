import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_HOST, CONF_PORT, CONF_CANAL, CONF_NUM_LUMINARIAS


class DaliGatewayConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self._data = {}

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_canal()

        schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Required(CONF_PORT, default=5000): int,
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_canal(self, user_input=None):
        errors = {}
        if user_input is not None:
            canal = user_input[CONF_CANAL]
            num_luminarias = user_input[CONF_NUM_LUMINARIAS]

            if not (1 <= canal <= 4):
                errors[CONF_CANAL] = "canal_invalido"
            elif not (1 <= num_luminarias <= 64):
                errors[CONF_NUM_LUMINARIAS] = "luminarias_invalido"
            else:
                self._data.update(user_input)
                host = self._data[CONF_HOST]
                # Unique ID por IP + canal para permitir varios canales en la misma IP
                await self.async_set_unique_id(f"{host}_canal{canal}")
                self._abort_if_unique_id_configured()
                title = f"Canal {canal} ({host})"
                return self.async_create_entry(title=title, data=self._data)

        schema = vol.Schema({
            vol.Required(CONF_CANAL): vol.All(int, vol.Range(min=1, max=4)),
            vol.Required(CONF_NUM_LUMINARIAS): vol.All(int, vol.Range(min=1, max=64)),
        })
        return self.async_show_form(step_id="canal", data_schema=schema, errors=errors)
