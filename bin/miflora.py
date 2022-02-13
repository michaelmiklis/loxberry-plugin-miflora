#!/usr/bin/python3
# encoding=utf-8

# 2018-07-03 Michael Miklis (michaelmiklis.de)


import time
import configparser
import json
import sys
import socket
import time
import os
import random
import argparse
import logging

from btlewrap import available_backends, BluepyBackend

from paho.mqtt import client as mqtt_client

from miflora.miflora_poller import MiFloraPoller, MI_CONDUCTIVITY, MI_MOISTURE, MI_LIGHT, MI_TEMPERATURE, MI_BATTERY
from miflora import miflora_scanner


def main(args):
    """
    Check if running in debug mode
    """
    if args.debug:
        import debugpy
        print("running in debug mode - waiting for debugger connection on {0}:{1}".format(args.debugip, args.debugport))
        debugpy.listen((args.debugip, args.debugport))
        debugpy.wait_for_client()

    """
    # Parse PlugIn config file
    """
    if not os.path.exists(args.configfile):
        logging.critical("Plugin configuration file missing {0}".format(args.configfile))
        sys.exit(-1)

    pluginconfig = configparser.ConfigParser()
    pluginconfig.read(args.configfile)
    enabled = pluginconfig.get('MIFLORA', 'ENABLED')
    miniservername = pluginconfig.get('MIFLORA', 'MINISERVER')
    virtualUDPPort = int(pluginconfig.get('MIFLORA', 'UDPPORT'))
    pollFrequency = int(pluginconfig.get('MIFLORA', 'POLLFREQUENCY'))
    localtime = pluginconfig.get('MIFLORA', 'LOCALTIME')
    scanTimeout = 10
    udpenabled = pluginconfig.get('MIFLORA', 'UDPENABLED')
    mqttenabled = pluginconfig.get('MIFLORA', 'MQTTENABLED')
    mqttbroker = pluginconfig.get('MIFLORA', 'MQTTBROKER')
    mqttport = int(pluginconfig.get('MIFLORA', 'MQTTPORT'))
    mqtttopic = pluginconfig.get('MIFLORA', 'MQTTTOPIC')
    mqttusername = pluginconfig.get('MIFLORA', 'MQTTUSERNAME')
    mqttpassword = pluginconfig.get('MIFLORA', 'MQTTPASSWORD')

    mqttclient_id = "loxberry-miflora-{0}".format(random.randint(0, 1000))


    """
    transistion from general.cfg to general.json
    """
    if miniservername.startswith("MINISERVER"):
        miniserverID = miniservername.replace("MINISERVER", "")

    else:
        miniserverID = miniservername
        miniservername = "MINISERVER{0}".format(miniserverID)

    """
    check if general.json exists and Loxberry version > 2.2
    """
    lbsConfigGeneralJSON = os.path.join(
        Config.Loxberry("LBSCONFIG"), "general.json")
    lbsConfigGeneralCFG = os.path.join(
        Config.Loxberry("LBSCONFIG"), "general.cfg")

    if not os.path.exists(lbsConfigGeneralJSON):
        logging.warning("gerneral.json missing in path {0}".format(lbsConfigGeneralJSON))
        logging.warning("trying general.cfg instead {0}".format(lbsConfigGeneralCFG))

        if not os.path.exists(lbsConfigGeneralCFG):
            logging.critical("general.cfg not found in path {0}".format(lbsConfigGeneralCFG))
            sys.exit(-1)

        """
        general.cfg (legacy configuration file)
        """
        logging.info("using system configuration file {0}/general.cfg".format(Config.Loxberry("LBSCONFIG")))
        loxberryconfig = configparser.ConfigParser()
        loxberryconfig.read("{0}/general.cfg".format(Config.Loxberry("LBSCONFIG")))
        miniserverIP = loxberryconfig.get(miniservername, 'IPADDRESS')

    else:
        with open(lbsConfigGeneralJSON, "r") as lbsConfigGeneralJSONHandle:
            logging.info("using system configuration file {0}/general.json".format(Config.Loxberry("LBSCONFIG")))
            data = json.load(lbsConfigGeneralJSONHandle)

        # check if miniserver from plugin config exists in general.json
        if not miniserverID in data["Miniserver"].keys():
            logging.critical("Miniserver with id {0} not found general.json - please check plugin configuration".format(miniserverID))
            sys.exit(-1)

        miniserverIP = data["Miniserver"][miniserverID]["Ipaddress"]
        logging.info("Miniserver ip address: {0}".format(miniserverIP))

    """
    global variables
    """
    lastdatafile = '{0}/{1}/{2}'.format(Config.Loxberry("LBPDATA"), "xiaomi-miflora", "lastdata.dat")

    """
    exit if PlugIn is not enabled
    """
    if enabled != "1":
        logging.warning("Plugin is not enabled in configuration - exiting")
        sys.exit(-1)

    """
    if called with argument "daemon"
    """
    if args.daemon:

        # check if it is time to run - otherwise exit
        if (int(time.strftime("%H")) / pollFrequency).is_integer() == False:
            sys.exit(-1)

    """
    MQTT connect
    """
    if mqttenabled == "1":
        mqttclient = connect_mqtt(mqttbroker, mqttport, mqttclient_id, mqttusername, mqttpassword)

    # ---------------------------------------------
    # scan for Xiaomi MiFlora device
    # ---------------------------------------------
    logging.info('Scanning for Xiaomi MiFlora devices (takes up to {0} seconds)'.format(scanTimeout))

    devices = miflora_scanner.scan(BluepyBackend, scanTimeout)

    logging.info('Found {0} devices:'.format(len(devices)))

    if len(devices) >= 1:
        """
        delete cached data file
        """
        if os.path.isfile(lastdatafile):
            os.remove(lastdatafile)

    """
    get data for each found sensor
    """
    for device in devices:
        devicemac = device.replace(":", "")

        logging.info('Polling device: {0}'.format(device))

        poller = MiFloraPoller(device, BluepyBackend)

        """
        Name
        """
        # build value string
        value = poller.name()

        # log data
        logging.info("{0}.{1}={2}".format(devicemac, "Name", value))

        # write value to lastdata.dat
        writelastdata(lastdatafile, "{0}.{1}={2}".format(devicemac, "Name", value))

        # send value as udp datagram
        if udpenabled == "1":
            sendudp("{0}.{1}={2}".format(devicemac, "Name", value), miniserverIP, virtualUDPPort)

        # publish MQTT topic
        if mqttenabled == "1":
            publish(mqttclient, "{0}/{1}/{2}".format(mqtttopic, devicemac, "Name"), value)

        """
        PollTime
        """
        # Calculate offset based on 01.01.2009
        loxBaseEpoch = 1230768000

        # Use current time as polling time
        pollTime = int(time.time())

        # Convert time to localtime if enabled
        if localtime == "1":
            pollLocalTime = time.localtime(pollTime)

            pollTime = pollTime + pollLocalTime.tm_gmtoff

        # Subtract time / date offset
        loxSensorTime = pollTime - loxBaseEpoch

        # build value strings
        value = "{0}.{1}={2}".format(devicemac, "PollTime", loxSensorTime)

        # log data
        logging.info(value)

        # write value to lastdata.dat
        writelastdata(lastdatafile, value)

        # send value as udp datagram
        if udpenabled == "1":
            sendudp(value, miniserverIP, virtualUDPPort)

        # publish MQTT topic
        if mqttenabled == "1":
            publish(mqttclient, "{0}/{1}/{2}".format(mqtttopic, devicemac, "PollTime"), loxSensorTime)

        """
        PollTimeString
        """
        # Use current time as polling time
        timestamp = time.strftime(
            "%d.%m.%Y %H:%M:%S", time.localtime(time.time()))

        # build value strings
        value = "{0}.{1}={2}".format(devicemac, "PollTimeString", timestamp)

        # log data
        logging.info(value)

        # write value to lastdata.dat
        writelastdata(lastdatafile, value)

        # send value as udp datagram
        if udpenabled == "1":
            sendudp(value, miniserverIP, virtualUDPPort)

        # publish MQTT topic
        if mqttenabled == "1":
            publish(mqttclient, "{0}/{1}/{2}".format(mqtttopic, devicemac, "PollTimeString"), timestamp)

        # -------------------------------
        # Firmware
        # -------------------------------
        # build value string
        value = poller.firmware_version()

        # log data
        logging.info("{0}.{1}={2}".format(devicemac, "Firmware", value))

        # write value to lastdata.dat
        writelastdata(lastdatafile, "{0}.{1}={2}".format(devicemac, "Firmware", value))

        # send value as udp datagram
        if udpenabled == "1":
            sendudp("{0}.{1}={2}".format(devicemac, "Firmware", value), miniserverIP, virtualUDPPort)

        # publish MQTT topic
        if mqttenabled == "1":
            publish(mqttclient, "{0}/{1}/{2}".format(mqtttopic, devicemac, "Firmware"), value)

        # -------------------------------
        # Temperature
        # -------------------------------
        # build value string
        value = poller.parameter_value(MI_TEMPERATURE)

        # log data
        logging.info("{0}.{1}={2}".format(devicemac, "Temperature", value))

        # write value to lastdata.dat
        writelastdata(lastdatafile, "{0}.{1}={2}".format(devicemac, "Temperature", value))

        # send value as udp datagram
        if udpenabled == "1":
            sendudp("{0}.{1}={2}".format(devicemac, "Temperature", value), miniserverIP, virtualUDPPort)

        # publish MQTT topic
        if mqttenabled == "1":
            publish(mqttclient, "{0}/{1}/{2}".format(mqtttopic, devicemac, "Temperature"), value)

        # -------------------------------
        # Moisture
        # -------------------------------
        # build value string
        value = poller.parameter_value(MI_MOISTURE)

        # log data
        logging.info("{0}.{1}={2}".format(devicemac, "Moisture", value))

        # write value to lastdata.dat
        writelastdata(lastdatafile, "{0}.{1}={2}".format(devicemac, "Moisture", value))

        # send value as udp datagram
        if udpenabled == "1":
            sendudp("{0}.{1}={2}".format(devicemac, "Moisture", value), miniserverIP, virtualUDPPort)

        # publish MQTT topic
        if mqttenabled == "1":
            publish(mqttclient, "{0}/{1}/{2}".format(mqtttopic, devicemac, "Moisture"), value)

        # -------------------------------
        # Light
        # -------------------------------
        # build value string
        value = poller.parameter_value(MI_LIGHT)

        # log data
        logging.info("{0}.{1}={2}".format(devicemac, "Light", value))

        # write value to lastdata.dat
        writelastdata(lastdatafile, "{0}.{1}={2}".format(devicemac, "Light", value))

        # send value as udp datagram
        if udpenabled == "1":
            sendudp("{0}.{1}={2}".format(devicemac, "Light", value), miniserverIP, virtualUDPPort)

        # publish MQTT topic
        if mqttenabled == "1":
            publish(mqttclient, "{0}/{1}/{2}".format(mqtttopic, devicemac, "Light"), value)

        # -------------------------------
        # Conductivity
        # -------------------------------
        # build value string
        value = poller.parameter_value(MI_CONDUCTIVITY)

        # log data
        logging.info("{0}.{1}={2}".format(devicemac, "Conductivity", value))

        # write value to lastdata.dat
        writelastdata(lastdatafile, "{0}.{1}={2}".format(devicemac, "Conductivity", value))

        # send value as udp datagram
        if udpenabled == "1":
            sendudp("{0}.{1}={2}".format(devicemac, "Conductivity", value), miniserverIP, virtualUDPPort)

        # publish MQTT topic
        if mqttenabled == "1":
            publish(mqttclient, "{0}/{1}/{2}".format(mqtttopic, devicemac, "Conductivity"), value)

        # -------------------------------
        # Battery
        # -------------------------------
        # build value string
        value = poller.parameter_value(MI_BATTERY)

        # log data
        logging.info("{0}.{1}={2}".format(devicemac, "Battery", value))

        # write value to lastdata.dat
        writelastdata(lastdatafile, "{0}.{1}={2}".format(devicemac, "Battery", value))

        # send value as udp datagram
        if udpenabled == "1":
            sendudp("{0}.{1}={2}".format(devicemac, "Battery", value), miniserverIP, virtualUDPPort)

        # publish MQTT topic
        if mqttenabled == "1":
            publish(mqttclient, "{0}/{1}/{2}".format(mqtttopic, devicemac, "Battery"), value)

        logging.info("-------------------------------------------------")

    # exit with errorlevel 0
    sys.exit(0)

# _______________________________________________________________________________________


def writelastdata(filename, data):
    lastdatahandle = open(filename, 'a')
    lastdatahandle.write("{0}\n".format(data))
    lastdatahandle.close()

# _______________________________________________________________________________________


def publish(client, topic, msg):

    result = client.publish(topic, msg)

    if result[0] == 0:
        logging.info("Send {0} to topic {1}".format(msg, topic))
    else:
        logging.error("Failed to send message to topic {0}".format(topic))

# _______________________________________________________________________________________


class Config:
    __loxberry = {
        "LBSCONFIG": os.getenv("LBSCONFIG", os.getcwd()),
        "LBPDATA": os.getenv("LBPDATA", os.getcwd()),
    }

    @staticmethod
    def Loxberry(name):
        return Config.__loxberry[name]

# _______________________________________________________________________________________


def connect_mqtt(broker, port, client_id, username, password):
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            logging.info("Connected to MQTT Broker!")
        else:
            logging.error("Failed to connect, return code {0}".format(rc))

    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)

    return client

# _______________________________________________________________________________________


def sendudp(data, destip, destport):
    # start a new connection udp connection
    connection = socket.socket(socket.AF_INET,     # Internet
                               socket.SOCK_DGRAM)  # UDP

    # send udp datagram
    res = connection.sendto(data.encode(), (destip, destport))

    # close udp connection
    connection.close()

    # check if all bytes in resultstr were sent
    if res != data.encode().__len__():
        logging.error("Sent bytes do not match - expected {0} : got {1}".format(data.__len__(), res))
        logging.error("Packet-Payload {0}".format(data))
        sys.exit(-1)

# _______________________________________________________________________________________

# parse args and call main function
print('Number of arguments:', len(sys.argv), 'arguments.')
print('Argument List:', str(sys.argv))

if __name__ == "__main__":
    """
    Parse commandline arguments
    """
    parser = argparse.ArgumentParser(
        description="Loxberry Xiaomi Miflora Plugin. More information can be found on Github site https://github.com/michaelmiklis/loxberry-plugin-miflora")

    debugroup = parser.add_argument_group("debug")

    debugroup.add_argument("--debug",
                           dest="debug",
                           default=False,
                           action="store_true",
                           help="enable debug mode")

    debugroup.add_argument("--debugip",
                           dest="debugip",
                           default=socket.gethostbyname(socket.gethostname()),
                           action="store",
                           help="Local IP address to listen for debugger connections (default={0})".format(socket.gethostbyname(socket.gethostname())))

    debugroup.add_argument("--debugport",
                           dest="debugport",
                           default=5678,
                           action="store",
                           help="TCP port to listen for debugger connections (default=5678)")

    loggroup = parser.add_argument_group("log")

    loggroup.add_argument("--logfile",
                          dest="logfile",
                          default="xiaomi-miflora.log",
                          type=str,
                          action="store",
                          help="specifies logfile path")

    configgroup = parser.add_argument_group("config")

    configgroup.add_argument("--configfile",
                             dest="configfile",
                             default="miflora.cfg",
                             type=str,
                             action="store",
                             help="specifies plugin configuration file path")

    daemongroup = parser.add_argument_group("daemon")

    daemongroup.add_argument("--daemon",
                             dest="daemon",
                             default=False,
                             action="store_true",
                             help="Running in daemon mode (polling only with configured pollIntervall")

    args = parser.parse_args()

    """
    # logging configuration
    """
    logging.getLogger().setLevel(logging.DEBUG)
    logging.basicConfig(filename=args.logfile,
                        filemode='w',
                        level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',)

    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.NOTSET)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)
    logging.info("using plugin log file {0}".format(args.logfile))

    """
    call main function
    """
    try:
        main(args)
    except Exception as e:
        logging.critical(e, exc_info=True)
