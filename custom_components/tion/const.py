from homeassistant.const import Platform

DOMAIN = 'tion'
TION_API = "data_tion"
PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.CLIMATE]

# Units of measurment
CO2_PPM = "ppm"
HUM_PERCENT = "%"

# Device types
MAGICAIR_DEVICE = "magicair"
BREEZER_DEVICE = "breezer"
