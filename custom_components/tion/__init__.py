import logging

from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_SCAN_INTERVAL, CONF_FILE_PATH
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from tion import TionApi, Breezer, MagicAir

from .const import DOMAIN, PLATFORMS, TION_API, BREEZER_DEVICE, MAGICAIR_DEVICE

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):
    return True


def create_api(user, password, interval, auth_fname):
    return TionApi(user, password, min_update_interval_sec=interval, auth_fname=auth_fname)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # Setup DOMAIN as default
    hass.data.setdefault(TION_API, {})

    user_input = entry.data['user_input']

    api = await hass.async_add_executor_job(create_api,
                                            user_input[CONF_USERNAME],
                                            user_input[CONF_PASSWORD],
                                            user_input[CONF_SCAN_INTERVAL],
                                            user_input[CONF_FILE_PATH]
                                            )

    assert api.authorization, "Couldn't get authorisation data!"
    _LOGGER.info(f"Api initialized with authorization {api.authorization}")

    hass.data[TION_API][entry.entry_id] = api

    # Get the device registry
    device_registry = dr.async_get(hass)

    devices = await hass.async_add_executor_job(api.get_devices)
    for device in devices:
        if device.valid:
            device_type = BREEZER_DEVICE if type(device) == Breezer else (
                MAGICAIR_DEVICE if type(device) == MagicAir else None)
            if device_type:
                device_registry.async_get_or_create(
                    config_entry_id=entry.entry_id,
                    identifiers={(DOMAIN, device.guid)},
                    manufacturer="Tion",
                    name=device.name,
                )
            else:
                _LOGGER.info(f"Unused device {device}")
        else:
            _LOGGER.info(f"Skipped device {device}, because of 'valid' property")

    # Forward to sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True
