import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from datetime import timedelta
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_SCAN_INTERVAL, CONF_FILE_PATH
from homeassistant.helpers import discovery

DOMAIN = 'tion'
TION_API = "data_tion"

# Units of measurment
CO2_PPM = "ppm"
HUM_PERCENT = "%"

# Device types
MAGICAIR_DEVICE = "magicair"
BREEZER_DEVICE = "breezer"


_LOGGER = logging.getLogger(__name__)

DEFAULT_SCAN_INTERVAL = timedelta(minutes=1)
DEFAULT_AUTH_FNAME = "tion_auth"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.time_period,
                vol.Optional(CONF_FILE_PATH, default=DEFAULT_AUTH_FNAME): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


def setup(hass, config):
    """Set up Tion Component."""
    from tion import TionApi, Breezer, MagicAir
    auth_fname = hass.config.path("tion_auth") if config[DOMAIN][CONF_FILE_PATH] == DEFAULT_AUTH_FNAME else config[DOMAIN][CONF_FILE_PATH]
    api = TionApi(
        config[DOMAIN][CONF_USERNAME],
        config[DOMAIN][CONF_PASSWORD],
        min_update_interval_sec=(config[DOMAIN][CONF_SCAN_INTERVAL]).seconds,
        auth_fname=auth_fname
    )
    assert api.authorization, "Couldn't get authorisation data!"
    _LOGGER.info(f"Api initialized with authorization {api.authorization}")
    hass.data[TION_API] = api
    discovery_info = {}
    for device in api.get_devices():
        if device.valid:
            device_type = BREEZER_DEVICE if type(device) == Breezer else (MAGICAIR_DEVICE if type(device) == MagicAir else None)
            if device_type:
                if "sensor" not in discovery_info:
                    discovery_info["sensor"] = []
                discovery_info["sensor"].append({"type": device_type, "guid": device.guid})
                if device_type == BREEZER_DEVICE:
                    if "climate" not in discovery_info:
                        discovery_info["climate"] = []
                    discovery_info["climate"].append({"type": device_type, "guid": device.guid})
            else:
                _LOGGER.info(f"Unused device {device}")
        else:
            _LOGGER.info(f"Skipped device {device}, because of 'valid' property")
    for device_type, devices in discovery_info.items():
        discovery.load_platform(hass, device_type, DOMAIN, devices, config)
        _LOGGER.info(f"Found {len(devices)} {device_type} devices")
    # Return boolean to indicate that initialization was successful.
    return True
