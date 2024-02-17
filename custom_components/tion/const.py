from homeassistant.const import Platform

DOMAIN = 'tion'
TION_API = "data_tion"
PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.CLIMATE]

# Device types
MAGICAIR_DEVICE = "magicair"
BREEZER_DEVICE = "breezer"
