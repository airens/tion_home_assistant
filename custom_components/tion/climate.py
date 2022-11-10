"""Support for Tion breezer heater"""
import logging
from time import sleep

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVAC_MODE_FAN_ONLY,
    HVAC_MODE_HEAT,
    SUPPORT_FAN_MODE,
    SUPPORT_TARGET_TEMPERATURE,
    HVAC_MODE_OFF,
    FAN_OFF,
    FAN_AUTO,
    ATTR_HVAC_MODE
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    PRECISION_WHOLE,
    TEMP_CELSIUS,
    STATE_UNKNOWN,
)

_LOGGER = logging.getLogger(__name__)

from tion import Breezer

from . import TION_API


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up Tion climate platform."""
    tion = hass.data[TION_API]
    if discovery_info is None:
        return
    devices = []
    for device in discovery_info:
        devices.append(TionClimate(tion, device["guid"]))
    add_entities(devices)


class TionClimate(ClimateEntity):
    """Tuya climate devices,include air conditioner,heater."""

    def __init__(self, tion, guid):
        """Init climate device."""
        self._breezer: Breezer = tion.get_devices(guid=guid)[0]
        self._zone: Zone = tion.get_zones(guid=self._breezer.zone.guid)[0]

    @property
    def temperature_unit(self):
        """Return the unit of measurement used by the platform."""
        return TEMP_CELSIUS

    @property
    def unique_id(self):
        """Return a unique id identifying the entity."""
        return self._breezer.guid

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._breezer.name}"

    @property
    def hvac_mode(self):
        """Return current operation ie. heat, cool, idle."""
        if self._breezer.valid:
            if self._zone.mode == "manual" and not self._breezer.is_on:
                return HVAC_MODE_OFF
            elif self._breezer.heater_enabled:
                return HVAC_MODE_HEAT
            else:
                return HVAC_MODE_FAN_ONLY
        else:
            return STATE_UNKNOWN

    @property
    def hvac_modes(self):
        """Return the list of available operation modes."""
        _operations = [HVAC_MODE_OFF, HVAC_MODE_FAN_ONLY]
        if self._breezer.heater_installed:
            _operations.append(HVAC_MODE_HEAT)
        return _operations

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._breezer.t_out if self._breezer.valid else STATE_UNKNOWN

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._breezer.t_set if self._breezer.valid else STATE_UNKNOWN

    @property
    def target_temperature_step(self):
        """Return the supported step of target temperature."""
        return 1

    @property
    def fan_mode(self):
        """Return the fan setting."""
        if self._zone.mode == "auto":
            return FAN_AUTO
        elif not self._breezer.is_on:
            return FAN_OFF
        else:
            return self._breezer.speed

    @property
    def fan_modes(self):
        """Return the list of available fan modes."""
        _fan_modes = [FAN_OFF, FAN_AUTO]
        try:
            _fan_modes.extend(range(0, int(self._breezer.speed_limit) + 1))
        except Exception as e:
            _fan_modes.extend(range(0, 7))
            _LOGGER.info(f"breezer.speed_limit is \"{self._breezer.speed_limit}\", fan_modes set to 0-6")
        return _fan_modes

    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        if ATTR_TEMPERATURE in kwargs:
            self._breezer.t_set = int(kwargs[ATTR_TEMPERATURE])
            self._breezer.send()
        if ATTR_HVAC_MODE in kwargs:
            self.set_hvac_mode(kwargs[ATTR_HVAC_MODE])

    def set_fan_mode(self, fan_mode):
        """Set new target fan mode."""
        new_mode = "manual"
        new_speed = None
        new_min_speed = new_max_speed = None
        new_co2 = self._zone.target_co2
        new_gate = None
        if fan_mode == FAN_OFF:
            new_speed = 0
        elif fan_mode == FAN_AUTO:
            new_mode = "auto"
            new_min_speed = 0
            new_max_speed = 6
        else:
            if fan_mode.isdigit():  # 1-6
                new_speed = int(fan_mode)
            elif fan_mode.count('-') == 0 and fan_mode.count(':') == 1:  # speed:gate
                new_speed, new_gate = fan_mode.split(':')
                new_speed = int(new_speed)
                new_gate = int(new_gate)
            elif fan_mode.count('-') == 1:  # {min}-{max}
                new_mode = "auto"
                speeds = fan_mode
                if fan_mode.count(':') == 1:  # {min}-{max}:{co2}
                    speeds, new_co2 = fan_mode.split(':')
                new_min_speed, new_max_speed = speeds.split('-')
                new_min_speed = int(new_min_speed)
                new_max_speed = int(new_max_speed)
        if self._zone.mode != new_mode or self._zone.target_co2 != new_co2:
            if self._zone.mode != new_mode:
                _LOGGER.info(f"Setting zone mode to {new_mode}")
                self._zone.mode = new_mode
            if self._zone.target_co2 != new_co2:
                _LOGGER.info(f"Setting zone target co2 to {new_co2}")
                self._zone.target_co2 = new_co2
            self._zone.send()
        if new_mode == "manual":
            if new_speed is not None:
                _LOGGER.info(f"Setting breezer fan_mode to {new_speed}")
                self._breezer.speed = new_speed
                if new_gate is not None:
                    self._breezer.gate = new_gate
                self._breezer.send()
        else:  # auto
            if (new_min_speed is not None and new_max_speed is not None) and \
                    (self.speed_min_set != new_min_speed or self.speed_max_set != new_max_speed):
                _LOGGER.info(f"Sending breezer speeds {new_min_speed}-{new_max_speed}")
                self._breezer.speed_min_set = new_min_speed
                self._breezer.speed_max_set = new_max_speed
                self._breezer.send()

    def set_hvac_mode(self, hvac_mode):
        """Set new target operation mode."""
        _LOGGER.info(f"Setting hvac mode to {hvac_mode}")
        if hvac_mode == HVAC_MODE_OFF:
            self.set_fan_mode(FAN_OFF)
        elif hvac_mode == HVAC_MODE_HEAT:
            self._breezer.heater_enabled = True
            self._breezer.send()
        elif hvac_mode == HVAC_MODE_FAN_ONLY:
            self._breezer.heater_enabled = False
            self._breezer.send()

    def update(self):
        """Fetch new state data for the breezer.
        This is the only method that should fetch new data for Home Assistant.
        """
        self._zone.load()
        self._breezer.load()

    @property
    def supported_features(self):
        """Return the list of supported features."""
        supports = SUPPORT_FAN_MODE
        if self._breezer.heater_installed:
            supports |= SUPPORT_TARGET_TEMPERATURE
        return supports

    @property
    def mode(self) -> str:
        """Return the current mode"""
        return self._zone.mode if self._zone.valid else STATE_UNKNOWN

    @property
    def target_co2(self) -> str:
        """Return the current mode"""
        return self._zone.target_co2 if self._zone.valid else STATE_UNKNOWN

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        return self._breezer.t_min if self._breezer.valid else STATE_UNKNOWN

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return self._breezer.t_max if self._breezer.valid else STATE_UNKNOWN

    @property
    def speed(self) -> str:
        """Return the current speed."""
        return self._breezer.speed if self._breezer.valid else STATE_UNKNOWN

    @property
    def speed_min_set(self) -> str:
        """Return the minimum speed for auto mode"""
        return self._breezer.speed_min_set if self._breezer.valid else STATE_UNKNOWN

    @property
    def speed_max_set(self) -> str:
        """Return the maximum speed for auto mode"""
        return self._breezer.speed_max_set if self._breezer.valid else STATE_UNKNOWN

    @property
    def filter_need_replace(self) -> str:
        """Return filter_need_replace input_boolean"""
        return self._breezer.filter_need_replace if self._breezer.valid else STATE_UNKNOWN

    @property
    def t_in(self) -> str:
        """Return filter_need_replace input_boolean"""
        return self._breezer.t_in if self._breezer.valid else STATE_UNKNOWN

    @property
    def gate(self) -> str:
        """Return gate type"""
        return "inside" if self._breezer.gate == 0 else ("combined" if self._breezer.gate == 1 else ("outside" if self._breezer.gate == 2 else STATE_UNKNOWN))

    @property
    def state_attributes(self) -> dict:
        """Return optional state attributes."""
        data = super().state_attributes
        data["mode"] = self.mode
        data["target_co2"] = self.target_co2
        data["speed"] = self.speed
        data["speed_min_set"] = self.speed_min_set
        data["speed_max_set"] = self.speed_max_set
        data["filter_need_replace"] = self.filter_need_replace
        data["t_in"] = self.t_in
        data["gate"] = self.gate
        return data

    @property
    def icon(self):
        """Return the entity picture to use in the frontend, if any."""
        return "mdi:air-filter"

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._breezer.valid and self._zone.valid
