# DALI Gateway — Home Assistant Custom Component

Integración personalizada para Home Assistant que permite controlar sistemas de iluminación **DALI** (Digital Addressable Lighting Interface) a través de una pasarela TCP/IP.

---

## ¿Qué es DALI?

DALI es un protocolo estándar de control de iluminación profesional (IEC 62386). Permite controlar luminarias de forma individual o en grupos, ajustando el nivel de brillo con precisión.

Esta integración actúa como puente entre Home Assistant y los dispositivos DALI conectados a una pasarela de red (TCP/IP).

---

## Características

- Control de brillo individual por luminaria (0–255)
- Encendido y apagado por luminaria
- Switch de broadcast para controlar todas las luminarias de un canal a la vez
- Soporte de múltiples canales sobre una misma IP
- Configuración completamente desde la interfaz de Home Assistant (sin editar archivos)

---

## Protocolo de comunicación

Los comandos se envían como paquetes de **6 bytes** vía TCP:

```
[0x24, 0x5A, CANAL, DISPOSITIVO, ORDEN, 0xFF]
```

| Byte | Valor | Descripción |
|------|-------|-------------|
| 0 | `0x24` | Cabecera fija |
| 1 | `0x5A` | Cabecera fija |
| 2 | `0x01`–`0x04` | Número de canal |
| 3 | `0x00`–`0xFE` | Dirección del dispositivo |
| 4 | `0x00`–`0xFE` | Orden (brillo) o comando |
| 5 | `0xFF` | Fin de trama |

### Direccionamiento de dispositivos

Los dispositivos (luminarias) de un mismo canal se direccionan en hexadecimal de **2 en 2**, empezando desde `0x00`:

| Luminaria | Dirección hex |
|-----------|---------------|
| 1 | `0x00` |
| 2 | `0x02` |
| 3 | `0x04` |
| 4 | `0x06` |
| 5 | `0x08` |
| 6 | `0x0A` |
| … | … |

El **broadcast** usa la dirección `0xFF` y afecta a todas las luminarias del canal.

---

## Instalación

### Instalación manual

1. Copia la carpeta `dali_gateway` dentro de tu directorio `custom_components` de Home Assistant:

```
config/
└── custom_components/
    └── dali_gateway/
        ├── __init__.py
        ├── config_flow.py
        ├── const.py
        ├── light.py
        ├── switch.py
        ├── manifest.json
        └── translations/
            ├── es.json
            └── en.json
```

2. Reinicia Home Assistant.

3. Ve a **Ajustes → Integraciones → Añadir integración** y busca **DALI Gateway**.

### Instalación con HACS (próximamente)

> Soporte HACS en desarrollo.

---

## Configuración

La integración se configura en **dos pasos** desde la interfaz de Home Assistant.

### Paso 1 — Pasarela

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| Dirección IP | IP de la pasarela DALI | `192.168.1.100` |
| Puerto | Puerto TCP de la pasarela | `5000` |

### Paso 2 — Canal

| Campo | Descripción | Rango |
|-------|-------------|-------|
| Número de canal | Canal DALI a configurar | 1 – 4 |
| Número de luminarias | Cantidad de luminarias en ese canal | 1 – 64 |

Una vez configurado, aparecerá una entrada llamada **"Canal X (IP)"** con:

- **N entidades de luz** → `Canal X Luminaria 1`, `Canal X Luminaria 2`…
- **1 switch de broadcast** → `Canal X Broadcast`

### Múltiples canales en la misma IP

Es posible añadir varios canales sobre la misma pasarela. Cada canal se registra como una entrada independiente, identificada por la combinación `IP + canal`, por lo que no habrá conflictos.

---

## Entidades generadas

### Luces (`light`)

Cada luminaria aparece como una entidad de tipo `light` con soporte de **brillo**:

- `light.canal_1_luminaria_1`
- `light.canal_1_luminaria_2`
- …

### Switch de broadcast (`switch`)

Cada canal genera también un switch que envía comandos a **todas las luminarias del canal** a la vez (dirección `0xFF`):

- `switch.canal_1_broadcast`

---

## Estructura del proyecto

```
dali_gateway/
├── __init__.py        # Inicialización y ciclo de vida de la integración
├── config_flow.py     # Flujo de configuración en 2 pasos (UI)
├── const.py           # Constantes del dominio
├── light.py           # Entidades de luz + clase DaliGateway (TCP)
├── switch.py          # Entidades switch (broadcast)
├── manifest.json      # Metadatos de la integración
└── translations/
    ├── es.json        # Textos en español
    └── en.json        # Textos en inglés
```

---

## Requisitos

- Home Assistant 2023.x o superior
- Pasarela DALI accesible por red TCP/IP
- Python 3.11+

---

## Limitaciones conocidas

- El estado de las luminarias es **optimista** (no se consulta el estado real al gateway, solo se refleja el último comando enviado).
- No se realiza autodescubrimiento de dispositivos DALI; el número de luminarias se indica manualmente.

---

## Licencia

MIT License. Consulta el archivo `LICENSE` para más detalles.
