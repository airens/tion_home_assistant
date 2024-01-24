# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.05] - 2024-01-24
### Added
- Поменял управление потоком воздуха. 
  Сейчас управления потоком сделано через свойство SWING (Режим качания). 
     SWING_VERTICAL = воздух из квартиры
     SWING_BOTH = смешанный
     SWING_HORIZONTAL = воздух с улицы

- Добавил дополнительные функции в соотвествии с шаблоном Climate.
  turn_aux_heat_on и turn_aux_heat_off
  Которые соответственно включают и выключают обогреватель из GUI.

- Переделал все пресеты на более нормальные, которые как-то соответствуют названию:
    PRESET_SLEEP:    с улицы,     скорость 1, обогреватель выключен
    PRESET_ACTIVITY: с улицы,     скорость 2, обогреватель выключен
    PRESET_BOOST:    с улицы,     скорость 6, обогреватель выключен
    PRESET_HOME:     из квартиры, скорость 2, обогреватель выключен           
    PRESET_COMFORT:  смешанный,   скорость 3, обогреватель выключен 
    PRESET_AWAY:     с улицы,     скорость 1, обогреватель выключен


## [1.03] - 2022-11-10
### Added
- библиотека Tion обновлена до 1.28. Исправлена работа 4S с нагревателем

## [1.02] - 2022-11-10
### Added
- библиотека Tion обновлена до 1.27

## [1.01] - 2022-11-10
### Added
- добавлена поддержка HVAC_MODE_OFF, версия библиотеки tion обновлена до 1.26
