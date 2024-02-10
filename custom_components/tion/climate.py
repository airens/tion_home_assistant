"""Support for Tion breezer heater"""
import logging

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVACMode,
    ClimateEntityFeature,
    FAN_OFF,
    FAN_AUTO,
    ATTR_HVAC_MODE,
    PRESET_AWAY,
    PRESET_COMFORT,
    PRESET_HOME,
    PRESET_ACTIVITY,
    PRESET_SLEEP,
    PRESET_BOOST,
    PRESET_NONE,
    PRESET_ECO,
    SWING_VERTICAL,
    SWING_HORIZONTAL,
    SWING_BOTH,
)
from homeassistant.const import (
    UnitOfTemperature,
    ATTR_TEMPERATURE,
    STATE_UNKNOWN,
)

from tion import (
    Breezer,
    Zone,
)

from . import TION_API

_LOGGER = logging.getLogger(__name__)


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
    """Tion climate devices,include air conditioner,heater."""

    def __init__(self, tion, guid):
        """Init climate device."""
        self._breezer: Breezer = tion.get_devices(guid=guid)[0]
        self._zone: Zone = tion.get_zones(guid=self._breezer.zone.guid)[0]
        self.preset = PRESET_NONE

    def turn_aux_heat_on(self):
        """Turn auxiliary heater on."""
        pass

    def turn_aux_heat_off(self):
        """Turn auxiliary heater off."""
        pass

    def turn_on(self) -> None:
        self._breezer.speed = 1
        self._breezer.send()

    def turn_off(self) -> None:
        self._breezer.speed = 0
        self._breezer.send()

    def set_swing_mode(self, swing_mode: str) -> None:
        """Set new preset mode"""
        if swing_mode == SWING_VERTICAL:
            self._breezer.gate = 0
        elif swing_mode == SWING_BOTH:
            self._breezer.gate = 1
        elif swing_mode == SWING_HORIZONTAL:
            self._breezer.gate = 2
        else:
            self._breezer.gate = 2
        _LOGGER.info(f"Device: {self._breezer.name} Swing mode changed to \"{swing_mode}\"")
        self._breezer.send()

    @property
    def temperature_unit(self):
        """Return the unit of measurement used by the platform."""
        return UnitOfTemperature.CELSIUS

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
                return HVACMode.OFF
            elif self._breezer.heater_enabled:
                return HVACMode.HEAT
            else:
                return HVACMode.FAN_ONLY
        else:
            return STATE_UNKNOWN

    @property
    def hvac_modes(self):
        """Return the list of available operation modes."""
        _operations = [HVACMode.OFF, HVACMode.FAN_ONLY]
        if self._breezer.heater_installed:
            _operations.append(HVACMode.HEAT)
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
            return str(int(self._breezer.speed))

    @property
    def fan_modes(self):
        """Return the list of available fan modes."""
        _fan_modes = [FAN_OFF, FAN_AUTO, 1, 2, 3, 4, 5, 6]
        # try:
        #     _fan_modes.extend(range(0, int(self._breezer.speed_limit) + 1))
        # except Exception as e:
        #     _fan_modes.extend(range(0, 7))
        #     _LOGGER.info(f"Device: {self._breezer.name} breezer.speed_limit is \"{self._breezer.speed_limit}\",
        #                  fan_modes set to 0-6")

        return [str(m) for m in _fan_modes]

    @property
    def preset_mode(self):
        """Return the preset mode. """
        _LOGGER.info(f"Device: {self._breezer.name} Preset is \"{self.preset}\"")
        return self.preset

    @property
    def preset_modes(self):
        """Return the list of available preset modes."""
        _preset_modes = [PRESET_SLEEP, PRESET_ACTIVITY, PRESET_HOME, PRESET_COMFORT, PRESET_BOOST, PRESET_ECO,
                         PRESET_AWAY, PRESET_NONE]
        return [str(m) for m in _preset_modes]

    @property
    def swing_mode(self):
        """Return the swing mode. It's 3 type: inside, outside, mixed"""
        """SWING_VERTICAL = get air from inside """
        """SWING_BOTH = get air from mixed """
        """SWING_HORIZONTAL = get air from outside """
        if self._breezer.gate == 0:
            """Inside"""
            _swing_mode = SWING_VERTICAL
        elif self._breezer.gate == 1:
            """Mixed"""
            _swing_mode = SWING_BOTH
        elif self._breezer.gate == 2:
            """Outside"""
            _swing_mode = SWING_HORIZONTAL
        else:
            _swing_mode = SWING_HORIZONTAL
        _LOGGER.info(f"Device: {self._breezer.name} Swing mode is \"{_swing_mode}\"")
        return _swing_mode

    @property
    def swing_modes(self):
        """Return the list of available preset modes."""
        """Return the preset modes. It's 3 type: inside, outside, mixed"""
        """SWING_VERTICAL = get air from inside """
        """SWING_BOTH = get air from mixed """
        """SWING_HORIZONTAL = get air from outside """
        _swing_modes = [SWING_VERTICAL, SWING_HORIZONTAL, SWING_BOTH]
        return [str(m) for m in _swing_modes]

    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        _LOGGER.info(f"Device: {self._breezer.name} Start setting set_temperature mode to {kwargs}")
        if ATTR_TEMPERATURE in kwargs:
            self._breezer.t_set = int(kwargs[ATTR_TEMPERATURE])
            self._breezer.send()
        if ATTR_HVAC_MODE in kwargs:
            self.set_hvac_mode(kwargs[ATTR_HVAC_MODE])

    def set_fan_mode(self, fan_mode):
        """Set new target fan mode."""
        _LOGGER.info(f"Device: {self._breezer.name} Start setting fan_mode mode to {fan_mode}")
        new_mode = "manual"
        new_speed = None

        if fan_mode == FAN_OFF:
            new_speed = 0
            _LOGGER.info(f"Device: {self._breezer.name} Setting fan mode to OFF")
        elif fan_mode == FAN_AUTO:
            if self._breezer.zone.valid:
                new_mode = "auto"
                self._breezer.zone.mode = "auto"
                self._breezer.zone.target_co2 = 600
                self._breezer.zone.send()

                self._breezer.speed_min_set = 1
                self._breezer.speed_max_set = 6
                self._breezer.heater_enabled = False
                _LOGGER.info(f"Device: {self._breezer.name} Setting fan mode to AUTO (1-6 speed)")
                self._breezer.send()
            else:
                _LOGGER.info(f"Error setting fan mode to AUTO. Need zone with MagicAir assigned!")
        else:
            _LOGGER.info(f"Device: {self._breezer.name} Setting fan mode to {fan_mode}")
            new_speed = int(fan_mode)

        if new_mode == "manual":
            if new_speed is not None:
                _LOGGER.info(f"Device: {self._breezer.name} Setting breezer fan_mode to {new_speed}")
                if self._breezer.zone.valid:
                    self._breezer.zone.mode = "manual"
                    self._breezer.zone.send()

                self._breezer.speed = new_speed
                self._breezer.send()

    def set_preset_mode(self, preset_mode):
        auto = False
        """Set new preset mode"""
        if preset_mode == PRESET_SLEEP:
            self._breezer.gate = 2
            self._breezer.speed = 1
            self._breezer.heater_enabled = False
            self.preset = PRESET_SLEEP
        elif preset_mode == PRESET_ACTIVITY:
            self._breezer.gate = 2
            self._breezer.speed = 2
            self._breezer.heater_enabled = False
            self.preset = PRESET_ACTIVITY
        elif preset_mode == PRESET_BOOST:
            self._breezer.gate = 2
            self._breezer.speed = 6
            self._breezer.heater_enabled = False
            self.preset = PRESET_BOOST
        elif preset_mode == PRESET_HOME:
            self._breezer.gate = 0
            self._breezer.speed = 2
            self._breezer.heater_enabled = False
            self.preset = PRESET_HOME

        elif preset_mode == PRESET_COMFORT:
            self._breezer.gate = 1
            self._breezer.speed = 3
            self._breezer.heater_enabled = False
            self.preset = PRESET_COMFORT
        elif preset_mode == PRESET_AWAY:
            auto = True
            self._breezer.zone.target_co2 = 600
            self._breezer.speed_min_set = 1
            self._breezer.speed_max_set = 6
            self._breezer.heater_enabled = False
            self.preset = PRESET_AWAY

        elif preset_mode == PRESET_ECO:
            auto = True
            self._breezer.zone.target_co2 = 700
            self._breezer.speed_min_set = 1
            self._breezer.speed_max_set = 4
            self._breezer.heater_enabled = False
            self.preset = PRESET_ECO

        elif preset_mode == PRESET_NONE:
            self.preset = PRESET_NONE

        else:
            new_gate = 2
            self._breezer.gate = new_gate
            self.preset = PRESET_NONE

        _LOGGER.info(f"Device: {self._breezer.name} Change preset to \"{preset_mode}\"")
        if not auto:
            self._breezer.zone.mode = "manual"
            self._breezer.zone.send()
            self._breezer.send()
        else:
            self._breezer.gate = 2
            self._breezer.zone.mode = "auto"
            self._breezer.zone.send()
            self._breezer.send()

    def set_hvac_mode(self, hvac_mode):
        """Set new target operation mode."""
        _LOGGER.info(f"Device: {self._breezer.name} Setting hvac mode to {hvac_mode}")
        if hvac_mode == HVACMode.OFF:
            self.set_fan_mode(FAN_OFF)
        elif hvac_mode == HVACMode.HEAT:
            self._breezer.heater_enabled = True
            if self._breezer.speed == 0:
                self._breezer.speed = 1
            self._breezer.send()
        elif hvac_mode == HVACMode.FAN_ONLY:
            self._breezer.heater_enabled = False
            if self._breezer.speed == 0:
                self._breezer.speed = 1
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
        supports = ClimateEntityFeature.FAN_MODE
        supports |= ClimateEntityFeature.PRESET_MODE
        supports |= ClimateEntityFeature.SWING_MODE
        supports |= ClimateEntityFeature.TURN_OFF
        supports |= ClimateEntityFeature.TURN_ON
        if self._breezer.heater_installed:
            supports |= ClimateEntityFeature.TARGET_TEMPERATURE
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
        if self._breezer.gate == 0:
            gate = "inside"
        elif self._breezer.gate == 1:
            gate = "combined"
        elif self._breezer.gate == 2:
            gate = "outside"
        else:
            gate = STATE_UNKNOWN
        return gate

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
