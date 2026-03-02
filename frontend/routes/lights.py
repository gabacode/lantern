from fastapi import APIRouter

from schemas.lights import IntensityPayload, RGBPayload, TemperaturePayload
from services import light_registry

router = APIRouter(prefix="/lights", tags=["lights"])


@router.get("")
async def get_lights():
    return {"lights": light_registry.list_lights()}


@router.post("/discover")
async def discover():
    """Scan for Yongnuo lights and add any new ones to the registry."""
    await light_registry.discover()
    return {"lights": light_registry.list_lights()}


@router.post("/{mac}/connect")
async def connect(mac: str):
    await light_registry.connect(mac)
    return {"status": "connected"}


@router.post("/{mac}/disconnect")
async def disconnect(mac: str):
    await light_registry.disconnect(mac)
    return {"status": "disconnected"}


@router.post("/{mac}/color")
async def set_color(mac: str, payload: RGBPayload):
    light_registry.require_connected(mac)
    light = light_registry.get_light(mac)
    light.color = (payload.r, payload.g, payload.b)
    await light.update()
    return {"status": "ok"}


@router.post("/{mac}/temperature")
async def set_temperature(mac: str, payload: TemperaturePayload):
    light_registry.require_connected(mac)
    light = light_registry.get_light(mac)
    light.color_temperature = payload.kelvin
    await light.update()
    return {"status": "ok"}


@router.post("/{mac}/intensity")
async def set_intensity(mac: str, payload: IntensityPayload):
    light_registry.require_connected(mac)
    light = light_registry.get_light(mac)
    light.intensity = payload.value
    await light.update()
    return {"status": "ok"}


@router.post("/{mac}/power_off")
async def power_off(mac: str):
    light_registry.require_connected(mac)
    light = light_registry.get_light(mac)
    await light.power_off()
    return {"status": "ok"}
