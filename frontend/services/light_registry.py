from fastapi import HTTPException

from lantern import Light


# MAC address -> Light instance
_lights: dict[str, Light] = {}
# MAC address -> connection state
_connected: dict[str, bool] = {}


async def discover():
    """Scan for Yongnuo lights and register any new ones found."""
    found = await Light.discover()
    for light in found:
        if light._mac not in _lights:
            _lights[light._mac] = light
            _connected[light._mac] = False


def list_lights() -> list[dict]:
    return [
        {"mac": mac, "connected": _connected.get(mac, False)}
        for mac in _lights
    ]


def get_light(mac: str) -> Light:
    light = _lights.get(mac)
    if light is None:
        raise HTTPException(status_code=404, detail="Light not found")
    return light


def require_connected(mac: str):
    if not _connected.get(mac):
        raise HTTPException(status_code=409, detail="Light is not connected")


async def connect(mac: str):
    light = get_light(mac)
    if _connected.get(mac):
        return
    await light.connect()
    _connected[mac] = True


async def disconnect(mac: str):
    light = get_light(mac)
    if not _connected.get(mac):
        return
    await light.disconnect()
    _connected[mac] = False
