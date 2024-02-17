"""Platform for sensor integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.sensor import ATTR_STATE_CLASS as STATE_CLASS
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
    SensorEntity,
)
from homeassistant.const import UnitOfTemperature, STATE_UNKNOWN, STATE_ON, STATE_OFF

from .const import DOMAIN
from tion import (
    Breezer,
    MagicAir,
    TionApi
)

_LOGGER = logging.getLogger(__name__)

from . import TION_API

# Sensor types
CO2_SENSOR = {
    "name": "co2",
    "native_unit_of_measurement": "ppm",
    STATE_CLASS: SensorStateClass.MEASUREMENT,
    "device_class": SensorDeviceClass.CO2,
    "suggested_display_precision": 0,
}
TEMP_SENSOR = {
    "name": "temperature",
    "native_unit_of_measurement": UnitOfTemperature.CELSIUS,
    STATE_CLASS: SensorStateClass.MEASUREMENT,
    "device_class": SensorDeviceClass.TEMPERATURE,
    "suggested_display_precision": 0,
}
HUM_SENSOR = {
    "name": "humidity",
    "native_unit_of_measurement": "%",
    STATE_CLASS: SensorStateClass.MEASUREMENT,
    "device_class": SensorDeviceClass.HUMIDITY,
    "suggested_display_precision": 0,
}
TEMP_IN_SENSOR = {
    "name": "temperature in",
    "native_unit_of_measurement": UnitOfTemperature.CELSIUS,
    STATE_CLASS: SensorStateClass.MEASUREMENT,
    "device_class": SensorDeviceClass.TEMPERATURE,
    "suggested_display_precision": 0,
}
TEMP_OUT_SENSOR = {
    "name": "temperature out",
    "native_unit_of_measurement": UnitOfTemperature.CELSIUS,
    STATE_CLASS: SensorStateClass.MEASUREMENT,
    "device_class": SensorDeviceClass.TEMPERATURE,
    "suggested_display_precision": 0,
}
SPEED_SENSOR = {
    "name": "speed",
    STATE_CLASS: SensorStateClass.MEASUREMENT,
    "suggested_display_precision": 0,
}
FAN_STATE_SENSOR = {
    "name": "fan state",
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
        if sensor_type.get(STATE_CLASS, None) is not None:
            self._attr_state_class = sensor_type[STATE_CLASS]
        if sensor_type.get('device_class', None) is not None:
            self._attr_device_class = sensor_type['device_class']
        if sensor_type.get('native_unit_of_measurement', None) is not None:
            self._attr_native_unit_of_measurement = sensor_type['native_unit_of_measurement']
        if sensor_type.get('suggested_display_precision', None) is not None:
            self._attr_suggested_display_precision = sensor_type['suggested_display_precision']

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
    def native_value(self):
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
            state = STATE_ON if self._device.speed > 0 else STATE_OFF
        return state if self._device.valid else STATE_UNKNOWN

    def update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        self._device.load()
