import asyncio
import logging
from homeassistant.components.light import LightEntity, ColorMode, ATTR_BRIGHTNESS
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN, CONF_HOST, CONF_CANAL, CONF_NUM_LUMINARIAS

_LOGGER = logging.getLogger(__name__)


class DaliGateway:
    """Gestiona la conexión TCP y la cola de comandos."""

    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._queue = asyncio.Queue()
        self._task = None

    def start(self):
        self._task = asyncio.ensure_future(self._worker())

    async def stop(self):
        if self._task:
            self._task.cancel()

    async def send(self, canal, dispositivo, orden):
        await self._queue.put((canal, dispositivo, orden))

    async def _worker(self):
        while True:
            canal, dispositivo, orden = await self._queue.get()
            payload = bytes([0x24, 0x5A, int(canal), int(dispositivo), int(orden), 0xFF])
            try:
                reader, writer = await asyncio.open_connection(self._host, self._port)
                writer.write(payload)
                await writer.drain()
                writer.close()
                await writer.wait_closed()
                _LOGGER.debug("DALI enviado: %s", " ".join(f"{b:02X}" for b in payload))
            except Exception as e:
                _LOGGER.error("Error enviando comando DALI: %s", e)
            finally:
                self._queue.task_done()
            await asyncio.sleep(0.0001)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    gateway = hass.data[DOMAIN][entry.entry_id]["gateway"]
    host = entry.data[CONF_HOST]
    canal = entry.data[CONF_CANAL]
    num_luminarias = entry.data[CONF_NUM_LUMINARIAS]

    # Los dispositivos van en hex de 2 en 2: 0x00, 0x02, 0x04...
    lights = [
        DaliLight(
            gateway=gateway,
            name=f"Canal {canal} Luminaria {i + 1}",
            host=host,
            canal=canal,
            dispositivo=i * 2,
        )
        for i in range(num_luminarias)
    ]
    async_add_entities(lights)


class DaliLight(LightEntity):
    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}

    def __init__(self, gateway, name, host, canal, dispositivo):
        self._gateway = gateway
        self._attr_name = name
        self._canal = canal
        self._dispositivo = dispositivo
        self._brightness = 0
        self._is_on = False
        self._attr_unique_id = f"dali_{host}_{canal}_{dispositivo:02X}"

    @property
    def is_on(self):
        return self._is_on

    @property
    def brightness(self):
        return self._brightness

    async def async_turn_on(self, **kwargs):
        brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
        orden = round(brightness * 0xFE / 255)
        self._brightness = brightness
        self._is_on = True
        await self._gateway.send(self._canal, self._dispositivo, orden)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        self._is_on = False
        self._brightness = 0
        await self._gateway.send(self._canal, self._dispositivo, 0x00)
        self.async_write_ha_state()
