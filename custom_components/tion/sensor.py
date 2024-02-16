"""Platform for sensor integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.sensor import ATTR_STATE_CLASS as STATE_CLASS
from homeassistant.components.sensor import (
    SensorStateClass,
    SensorEntity,
)
from homeassistant.const import UnitOfTemperature, STATE_UNKNOWN

from .const import CO2_PPM, HUM_PERCENT, DOMAIN
from tion import (
    Breezer,
    MagicAir,
    TionApi
)

_LOGGER = logging.getLogger(__name__)

from . import TION_API

# Sensor types
CO2_SENSOR = {
    "unit": CO2_PPM,
    "name": "co2",
    STATE_CLASS: SensorStateClass.MEASUREMENT,
}
TEMP_SENSOR = {
    "unit": UnitOfTemperature.CELSIUS,
    "name": "temperature",
    STATE_CLASS: SensorStateClass.MEASUREMENT,
}
HUM_SENSOR = {
    "unit": HUM_PERCENT,
    "name": "humidity",
    STATE_CLASS: SensorStateClass.MEASUREMENT,
}
TEMP_IN_SENSOR = {
    "unit": UnitOfTemperature.CELSIUS,
    "name": "temperature in",
    STATE_CLASS: SensorStateClass.MEASUREMENT,
}
TEMP_OUT_SENSOR = {
    "unit": UnitOfTemperature.CELSIUS,
    "name": "temperature out",
    STATE_CLASS: SensorStateClass.MEASUREMENT,
}
SPEED_SENSOR = {
    "unit": "",
    "name": "speed",
    STATE_CLASS: SensorStateClass.MEASUREMENT,
}
FAN_STATE_SENSOR = {
    "name": "fan state",
    STATE_CLASS: None,
}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> bool:
    tion = hass.data[TION_API][entry.entry_id]

    entities = []
    devices = await hass.async_add_executor_job(tion.get_devices)
    for device in devices:
        if device.valid:
            if type(device) == MagicAir:
                entities.append(TionSensor(tion, device.guid, CO2_SENSOR))
                entities.append(TionSensor(tion, device.guid, TEMP_SENSOR))
                entities.append(TionSensor(tion, device.guid, HUM_SENSOR))
            elif type(device) == Breezer:
                entities.append(TionSensor(tion, device.guid, TEMP_IN_SENSOR))
                entities.append(TionSensor(tion, device.guid, TEMP_OUT_SENSOR))
                entities.append(TionSensor(tion, device.guid, SPEED_SENSOR))
                entities.append(TionSensor(tion, device.guid, FAN_STATE_SENSOR))
        else:
            _LOGGER.info(f"Skipped device {device}, because of 'valid' property")

    async_add_entities(entities)
    return True


class TionSensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, tion: TionApi, guid, sensor_type):
        self._device = tion.get_devices(guid=guid)[0]
        self._sensor_type = sensor_type

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device.guid)},
        }

    @property
    def unique_id(self):
        """Return a unique id identifying the entity."""
        return self._device.guid + self._sensor_type["name"]

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
        elif self._sensor_type == SPEED_SENSOR:
            state = self._device.speed
        elif self._sensor_type == FAN_STATE_SENSOR:
            state = 'on' if self._device.speed > 0 else 'off'
        return state if self._device.valid else STATE_UNKNOWN

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        if self._sensor_type["name"] == "fan state":
            return None
        return self._sensor_type["unit"] if self._device.valid else None

    @property
    def state_class(self):
        """Return sensor state class"""
        return self._sensor_type[STATE_CLASS] if self._device.valid else None

    def update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        self._device.load()
