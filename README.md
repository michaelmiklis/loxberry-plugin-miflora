# Loxberry Plugin: Xiaomi MiFlora Flower Sensor
This Plugin queries the Xiaomi MiFlora Flower Sensors via bluetooth low energy (btle) and sends the data via UDP to the Loxone Miniserver.

<img src="https://raw.githubusercontent.com/michaelmiklis/loxberry-plugin-miflora/assets/plugin.png" height="600" alt="Xiaomi MiFlora Plugin"/>

The Xiaomi MiFlora Plugin supports multiple flower sensors. During each execution a bluetooth scan for Xiaomi MiFlora devices is performed and each found device will be queried. Each received value will be send as an individual UDP packet. The UDP packets will have the following format:

[Device-MAC].[Sensor-Name]=[Value]

Sample:

C47C8D66275B.Moisture=4
C47C8D66275B.Light=136

## Sample
The UDP packages will be sent as follows:

<img src="https://raw.githubusercontent.com/michaelmiklis/loxberry-plugin-miflora/assets/udp-monitor.png" alt="UDP-Monitor" height="300"/>

With the following command recognition the values can be assigend to a "UDP-Command" / virtual input:

<img src="https://raw.githubusercontent.com/michaelmiklis/loxberry-plugin-miflora/assets/command.png" alt="UDP-Befehl" width="350" />

## Sensor data

| Sensor Name             | Description                | Sample value            |
| ----------------------- | -------------------------- | ----------------------- |
| Name                    | Name of the sensor         | Flower care             |
| PollTime                | Date/Time in Loxone format | 297370058               |
| PollTimeString          | Date/Time string           | 03.06.2018 18:47:38     |
| Firmware                | Firmware version           | 2.7.0                   |
| Temperature             | Temperature in Celcius     | 27.1                    |
| Moisture                | Moisture (unknown unit)    | 4                       |
| Light                   | Light (unknown unit)       | 136                     |
| Conductivity            | Conductivity (unknown unit)| 0                       |
| Battery                 | Battery level in percent   | 86                      |


## Troubleshooting and feedback
If you have any issues you can run the plugin manually from the Loxberry command line (SSH) using the following command:
	/usr/bin/python3 /opt/loxberry/bin/plugins/xiaomi-miflora/miflora.py

This plugin will be improved over time and feedback is appreciated. Therefore I created a thread in the LoxForum:

!link will be added!

## Change-Log
- 2018-06-04 Release 1.0.0 - Initial release of version 1.0.0


## Known-Issues
- No logging
