# Tion Integration
This component provides integration of Tion devices (breezers and climate sensors) into Home Assistant smart home system. Based on the [tion](https://github.com/airens/tion) package.
## Configuration
```yaml
tion:
  username: !secret tion_email
  password: !secret tion_password
```
## Usage:
After restart you should see your breezer device as `climate.tion_...` and your MagicAir sensors as `sensor.magicair_..`. 
Services, allowed to control your breezer:
### climate.set_fan_mode 
`fan_mode` parameter defines the speed of the device in format:
- `off`, `0` - turned off
- `1`-`6` - on and manually controlled
- `auto` - automatic breezer control depending on the CO2 level
- `2-4`, `1-3`, `4-6`... etc - automatic control with set speed range
### climate.set_hvac_mode 
`hvac_mode` defines your breezer's heater state:
- `heat` - heater on
- `fan_only` - heater off
### climate.set_temperature 
can be used to set target temperature for heater by setting `temperature` parameter
## Troubleshooting
If something went wrong, turn on extended logs for this component and for the `tion` package in your `configuration.yaml`:
```yaml
logger:
  default: warning
  logs:
    custom_components.tion: info
    tion: info
```
<a href="https://www.buymeacoffee.com/3nCPSY4" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" style="height: 51px !important;width: 217px !important;" ></a>
