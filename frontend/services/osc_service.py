"""
OSC service — listens for OSC messages and maps them to light controls.
"""

import asyncio
import logging

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer

from services import light_registry

HOST = "0.0.0.0"
PORT = 9000

logger = logging.getLogger(__name__)


def _parse_mac(address: str) -> str:
    """Extract MAC from an address like /light/AA:BB:CC:DD:EE:FF/command."""
    return address.strip("/").split("/")[1]


def _handle_intensity(address: str, *args):
    mac = _parse_mac(address)
    value = float(args[0])
    asyncio.ensure_future(_set_intensity(mac, value))


def _handle_temperature(address: str, *args):
    mac = _parse_mac(address)
    kelvin = int(args[0])
    asyncio.ensure_future(_set_temperature(mac, kelvin))


def _handle_color(address: str, *args):
    mac = _parse_mac(address)
    r, g, b = int(args[0]), int(args[1]), int(args[2])
    asyncio.ensure_future(_set_color(mac, r, g, b))


def _handle_power_off(address: str, *args):
    mac = _parse_mac(address)
    asyncio.ensure_future(_power_off(mac))


async def _set_intensity(mac: str, value: float):
    try:
        await light_registry.connect(mac)
        light = light_registry.get_light(mac)
        light.intensity = value
        if light._color is not None:
            await light.update()
    except Exception as e:
        logger.warning("OSC intensity error [%s]: %s", mac, e)


async def _set_temperature(mac: str, kelvin: int):
    try:
        await light_registry.connect(mac)
        light = light_registry.get_light(mac)
        light.color_temperature = kelvin
        await light.update()
    except Exception as e:
        logger.warning("OSC temperature error [%s]: %s", mac, e)


async def _set_color(mac: str, r: int, g: int, b: int):
    try:
        await light_registry.connect(mac)
        light = light_registry.get_light(mac)
        light.color = (r, g, b)
        await light.update()
    except Exception as e:
        logger.warning("OSC color error [%s]: %s", mac, e)


async def _power_off(mac: str):
    try:
        await light_registry.connect(mac)
        light = light_registry.get_light(mac)
        await light.power_off()
    except Exception as e:
        logger.warning("OSC power_off error [%s]: %s", mac, e)


async def start() -> AsyncIOOSCUDPServer:
    """Start the OSC UDP server and return the transport (call transport.close() to stop)."""
    dispatcher = Dispatcher()
    dispatcher.map("/light/*/intensity", _handle_intensity)
    dispatcher.map("/light/*/temperature", _handle_temperature)
    dispatcher.map("/light/*/color", _handle_color)
    dispatcher.map("/light/*/power_off", _handle_power_off)

    server = AsyncIOOSCUDPServer((HOST, PORT), dispatcher, asyncio.get_event_loop())
    transport, _ = await server.create_serve_endpoint()
    logger.info("OSC server listening on %s:%d", HOST, PORT)
    return transport
