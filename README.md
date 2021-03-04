# Tion Home Assistant
Интеграция обеспечивает управление бризерами Tion, а также чтение показаний датчиков (включая датчики MagicAir) из системы умного дома Home Assistant. Основано на пакете [tion](https://github.com/airens/tion).

*Внимание: для работы требуется шлюз MagicAir!*
## Установка
### HACS:
1. HACS->Settings->Custom repositories 
2. Добавьте `airens/tion_home_assistant` в поле `ADD CUSTOM REPOSITORY` и выберите `Integration` в `CATEGORY`. Щелкните кнопку `Save`
### Без HACS:
1. скачайте zip файл с компонентом
2. поместите содержимое в `config/custom_components/tion` папку системы Home Assistant
### ...
3. добавьте в ваш файл конфигурации (`configuration.yaml`):
```yaml
tion:
  username: !secret tion_email
  password: !secret tion_password
```
4. не обязательно: можно задать периодичность опроса датчиков (по умолчанию - 120 секунд)
```yaml
  scan_interval: 600
```
5. не обязательно: можно задать альтернативный путь для файла-хранилища аутентификации (по умолчанию - "{homeassistant_config_dir}/tion_auth")
```yaml
  file_path: "/tmp/tion_auth"
```
6. добавьте `tion_email` и `tion_password` в ваще хранилище паролей Home Assistant `secrets.yaml`
7. перезагрузите Home Assistant
## Использование:
После перезагрузки, среди устройств должны появиться бризеры `climate.tion_...` и датчики MagicAir `sensor.magicair_..`.

Службы Home Assistant для управления вашими устройствами:
### climate.set_fan_mode
`fan_mode` задает скорость бризера следующим образом:
- `off`, `0` - выключить
- `1`-`6` - включить в ручном режиме с заданной скоростью
- `1`-`6`:`0`-`2` - включить в ручном режиме с заданной скоростью и задать откуда брать воздух (`0` - с улицы, `1` - смешанный, `2` - из дома)
- `auto` - автоматическое управление скоростью в зависимости от уровня CO2
- `2-4`, `1-3`, `4-6`... автоматическое управление в заданном диапазоне скоростей
- `2-4:800`, `1-3:900`, `4-6:1000`... автоматическое управление в заданном диапазоне скоростей с задачей целевого уровня CO2
### climate.set_hvac_mode
`hvac_mode` задает состояние нагревателя входящего воздуха:
- `heat` - нагреватель включен
- `fan_only` - нагреватель выключен
### climate.set_temperature
Используйте для задачи целевой температуры нагревателя
## Если что-то не работает
Включите расширенное логирование для интеграции и пакета `tion` в файле конфигурации `configuration.yaml`:
```yaml
logger:
  default: warning
  logs:
    custom_components.tion: info
    tion: info
```
