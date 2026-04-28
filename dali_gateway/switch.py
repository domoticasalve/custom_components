import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN, CONF_HOST, CONF_CANAL
from .light import DaliGateway

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    gateway = hass.data[DOMAIN][entry.entry_id]["gateway"]
    host = entry.data[CONF_HOST]
    canal = entry.data[CONF_CANAL]

    # Un switch de broadcast por canal (dispositivo 0xFF = todas las luminarias del canal)
    async_add_entities([
        DaliSwitch(gateway, f"Canal {canal} Broadcast", host, canal, 0xFF)
    ])


class DaliSwitch(SwitchEntity):

    def __init__(self, gateway: DaliGateway, name, host, canal, dispositivo):
        self._gateway = gateway
        self._attr_name = name
        self._canal = canal
        self._dispositivo = dispositivo
        self._is_on = False
        self._attr_unique_id = f"dali_switch_{host}_{canal}_{dispositivo:02X}"

    @property
    def is_on(self):
        return self._is_on

    async def async_turn_on(self, **kwargs):
        self._is_on = True
        await self._gateway.send(self._canal, self._dispositivo, 0x05)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        self._is_on = False
        await self._gateway.send(self._canal, self._dispositivo, 0x00)
        self.async_write_ha_state()
