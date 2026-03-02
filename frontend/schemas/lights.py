from pydantic import BaseModel


class RGBPayload(BaseModel):
    r: int
    g: int
    b: int


class TemperaturePayload(BaseModel):
    kelvin: int


class IntensityPayload(BaseModel):
    value: float


class LightState(BaseModel):
    mac: str
    connected: bool
