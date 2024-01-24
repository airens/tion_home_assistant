# ВНИМАНИЕ!!!
Это fork (доработанная копия) оригинального модуля Tion_Home_Assistant от Уважаемого Valeriy Chistyakov.
Большое спасибо ему за модуль, я только поправил кое-какие замечания по синтаксису, которые вылезли после обновления Home Assistant до версии 2024.01

# Tion Home Assistant
Интеграция обеспечивает управление бризерами Tion, а также чтение показаний датчиков (включая датчики MagicAir) из системы умного дома Home Assistant. Основано на пакете [tion](https://github.com/airens/tion).

*Внимание: для работы требуется шлюз MagicAir!*
## Установка
### HACS:
1. HACS->Settings->Custom repositories 
2. Добавьте `reallord/tion_home_assistant` в поле `ADD CUSTOM REPOSITORY` и выберите `Integration` в `CATEGORY`. Щелкните кнопку `Save`
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
`fan_mode` задает скорость бризера следующим образом (тип - строка):
- `off`, `0` - выключить
- `1`-`6` - включить в ручном режиме с заданной скоростью
- `auto` - автоматическое управление скоростью в зависимости от уровня CO2
  - определяется переменной target_co2
### climate.set_hvac_mode
`hvac_mode` задает режим работы прибора:
- `heat` - нагреватель включен
- `fan_only` - нагреватель выключен
- `off` - прибор выключен
### climate.set_temperature
Используйте для задачи целевой температуры нагревателя
### climate.set_swing
Используйте для задания источника потока воздуха: улица, квартира, смешанный
- SWING_VERTICAL = воздух из квартиры
- SWING_BOTH = смешанный
- SWING_HORIZONTAL = воздух с улицы
### climate.set_preset
Используйте для задания заранее запрограммированных настроек (пресетов)
- PRESET_SLEEP:    с улицы,     скорость 1, обогреватель выключен
- PRESET_ACTIVITY: с улицы,     скорость 2, обогреватель выключен
- PRESET_BOOST:    с улицы,     скорость 6, обогреватель выключен
- PRESET_HOME:     из квартиры, скорость 2, обогреватель выключен           
- PRESET_COMFORT:  смешанный,   скорость 3, обогреватель выключен 
- PRESET_AWAY:     с улицы,     скорость 1, обогреватель выключен

## Если что-то не работает
Включите расширенное логирование для интеграции и пакета `tion` в файле конфигурации `configuration.yaml`:
```yaml
logger:
  default: warning
  logs:
    custom_components.tion: info
    tion: info
```
