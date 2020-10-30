"""Platform for sensor integration."""
import logging
from homeassistant.const import TEMP_CELSIUS, STATE_UNKNOWN
from homeassistant.helpers.entity import Entity
from tion import MagicAir, Thermostat

_LOGGER = logging.getLogger(__name__)

from . import TION_API, BREEZER_DEVICE, MAGICAIR_DEVICE, CO2_PPM, HUM_PERCENT, THERMOSTAT_DEVICE

# Sensor types
CO2_SENSOR = {"unit": CO2_PPM, "name": "co2"}
TEMP_SENSOR = {"unit": TEMP_CELSIUS, "name": "temperature"}
HUM_SENSOR = {"unit": HUM_PERCENT, "name": "humidity"}
TEMP_IN_SENSOR = {"unit": TEMP_CELSIUS, "name": "temperature in"}
TEMP_OUT_SENSOR = {"unit": TEMP_CELSIUS, "name": "temperature out"}


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    tion = hass.data[TION_API]
    if discovery_info is None:
        return
    devices = []
    for device in discovery_info:
        if device["type"] == MAGICAIR_DEVICE:
            devices.append(TionSensor(tion, device["guid"], CO2_SENSOR))
            devices.append(TionSensor(tion, device["guid"], TEMP_SENSOR))
            devices.append(TionSensor(tion, device["guid"], HUM_SENSOR))
        elif device["type"] == BREEZER_DEVICE:
            devices.append(TionSensor(tion, device["guid"], TEMP_IN_SENSOR))
            devices.append(TionSensor(tion, device["guid"], TEMP_OUT_SENSOR))
        if device["type"] == THERMOSTAT_DEVICE:
            devices.append(TionSensor(tion, device["guid"], TEMP_SENSOR))         
    add_entities(devices)


class TionSensor(Entity):
    """Representation of a Sensor."""
    def __init__(self, tion, guid, sensor_type):
        self._device = tion.get_devices(guid=guid)[0]
        self._sensor_type = sensor_type

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._device.name} {self._sensor_type['name']}"

    @property
    def state(self):
        """Return the state of the sensor."""
        state = STATE_UNKNOWN
        if self._sensor_type == CO2_SENSOR:
            state = self._device.co2
        elif self._sensor_type == TEMP_SENSOR:
            state = self._device.temperature
        elif self._sensor_type == HUM_SENSOR:
            state = self._device.humidity
        elif self._sensor_type == TEMP_IN_SENSOR:
            state = self._device.t_in
        elif self._sensor_type == TEMP_OUT_SENSOR:
            state = self._device.t_out
        return state if self._device.valid else STATE_UNKNOWN

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._sensor_type["unit"] if self._device.valid else None

    def update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        self._device.load()