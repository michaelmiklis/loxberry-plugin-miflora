# Loxberry Plugin: Xiaomi MiFlora Flower Sensor

This Plugin queries the Xiaomi MiFlora Flower Sensors via bluetooth low energy (btle) and sends the data via UDP and MQTT (experimental support) to the Loxone Miniserver.

<img src="https://raw.githubusercontent.com/michaelmiklis/loxberry-plugin-miflora/assets/plugin.png" height="600" alt="Xiaomi MiFlora Plugin"/>

The Xiaomi MiFlora Plugin supports multiple flower sensors. During each execution a bluetooth scan for Xiaomi MiFlora devices is performed and each found device will be queried.

## UDP Mode (default)

Each received value will be send as an individual UDP packet. The UDP packets will have the following format:

[Device-MAC].[Sensor-Name]=[Value]

Sample:

C47C8D66275B.Moisture=4
C47C8D66275B.Light=136

The UDP packages will be sent as follows:

<img src="https://raw.githubusercontent.com/michaelmiklis/loxberry-plugin-miflora/assets/udp-monitor.png" alt="UDP-Monitor" height="300"/>

With the following command recognition the values can be assigend to a "UDP-Command" / virtual input:

<img src="https://raw.githubusercontent.com/michaelmiklis/loxberry-plugin-miflora/assets/command.png" alt="UDP-Befehl" width="350" />

## MQTT Mode (Experimental Support)

Starting in version 2.0.4 the Xiaomi MiFlora Flower Sensor Plugin also supports MQTT for sending data to the Loxone Miniserver. This requires the MQTT Gateway Plugin to be installed and successfully configured.
Further documentation and improvements on MQTT will be added in future releases.

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

`/usr/bin/python3 /opt/loxberry/bin/plugins/xiaomi-miflora/miflora.py`

If the above command does NOT find you Xiaomi Flower Sensors proceed with the following steps to find the cause:

### Step 1: Are the sensors are discoverable by the OS?

Test if the bluetooth stack from Raspbian can find the devices:

`hcitool lescan (must be executed as root)`

If your device is not found - it seems to be a low-level problem either with the bluetooth device, your raspbian drivers, bluetooth chip, e.g.
Please understand that I cannot provide support for these kind of problems as they are not related to the plugin.

### Step 2: Are the sesnors are discoverable by the Python btle-wrapper?

Start the btle-wrapper (called bluepy-helper). This module makes the bluetooth stack available in python3.

`./usr/local/lib/python3.7/dist-packages/bluepy/bluepy-helper`

Enter `scan` and check the output if your devices are listed here (rsp=$scanaddr=b{YOUR DEVICE ID}type)

If your device is not found or any module-errors are shown it seems to be a problem with the bluepy python3 moduel. Check the version and try to manually reinstall the module:

`pip3 show bluepy`
`apt-get install --no-install-recommends --reinstall python3-pip`

Please understand that I cannot provide support for these kind of problems as they are not related to the plugin.

### Step 3: Discover using pyhton3 script blescan

To start a discovery of the BLE devices using blescan.py execute the following command:

`python3 /usr/local/bin/blescan`

If your device is not found - it seems to be a problem with the bluepy python3 module.
Check the developers page <https://github.com/IanHarvey/bluepy> for further assistance.

### Step 4: Check Logfile in Loxberry WebUI

Navigate to "Log Manager" -> "More Logfiles" -> "Xiaomi Flower Monitor (Plugin Log)" and check the logfile for error messages.

### Step 5: Execute plugin locally using SSH connection

Open an SSH connection to your Loxberry and execute the following command:

`python3 /usr/bin/python3 /opt/loxberry/bin/plugins/xiaomi-miflora/miflora.py --logfile=/opt/loxberry/log/plugins/xiaomi-miflora/xiaomi-miflora.log --configfile=/opt/loxberry/config/plugins/xiaomi-miflora/miflora.cfg`

If python specific errors occur, they will be displayed in the console.

### Step 6: All of the above worked correctly, but the plugin still fails

Post an issue on my GitHub Page or in the Loxberry Forum.
<https://www.loxforum.com/forum/projektforen/loxberry/plugins/156917-plugin-xiaomi-miflora-flower-monitor>

## Feedback & Discussion

This plugin will be improved over time and feedback is appreciated. Therefore I created a thread in the LoxForum:

<https://www.loxforum.com/forum/projektforen/loxberry/plugins/156917-plugin-xiaomi-miflora-flower-monitor>

## Change-Log

- 2022-02-13 Release 2.0.4 - Added MQTT experimental MQTT functionality
- 2021-08-01 Release 2.0.3 - Fixed issue in WebUI with On/Off switches
- 2020-01-05 Release 2.0.2 - Fixed issue with btlewrap __init__
- 2019-12-31 Release 2.0.1 - Support for Loxberry 2.0.0.4 and above
- 2018-06-18 Release 1.0.1 - Fixed typo in postroot.sh install script
- 2018-06-04 Release 1.0.0 - Initial release of version 1.0.0

## Known-Issues

- No logging
