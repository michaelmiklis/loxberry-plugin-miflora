#!/usr/bin/python3
# encoding=utf-8

# 2018-07-03 Michael Miklis (michaelmiklis.de)


import time
import configparser
import urllib.parse
import requests
import json
import sys
import socket
import time
import os

from btlewrap import available_backends, BluepyBackend, GatttoolBackend, PygattBackend

from miflora.miflora_poller import MiFloraPoller, MI_CONDUCTIVITY, MI_MOISTURE, MI_LIGHT, MI_TEMPERATURE, MI_BATTERY
from miflora import miflora_scanner

def main():
    # ---------------------------------------------
    # Global variables
    # ---------------------------------------------
    lbpdatadir = "PLUGINDATAFOLDER"
    lastdatafile = '{0}{1}'.format(lbpdatadir, "/lastdata.dat")

    # ---------------------------------------------
    # Parse PlugIn config file
    # ---------------------------------------------
    pluginconfig = configparser.ConfigParser()
    pluginconfig.read("PLUGINCONFIGFOLDER/miflora.cfg")

    enabled = pluginconfig.get('MIFLORA', 'ENABLED')
    miniservername = pluginconfig.get('MIFLORA', 'MINISERVER')
    virtualUDPPort = int(pluginconfig.get('MIFLORA', 'UDPPORT'))
    pollFrequency = int(pluginconfig.get('MIFLORA', 'POLLFREQUENCY'))
    localtime = pluginconfig.get('MIFLORA', 'LOCALTIME')
    scanTimeout = 10


    # ---------------------------------------------
    # Parse Loxberry config file
    # ---------------------------------------------
    loxberryconfig = configparser.ConfigParser()
    loxberryconfig.read("SYSTEMCONFIGFOLDER/general.cfg")

    miniserverIP = loxberryconfig.get(miniservername, 'IPADDRESS')

    # ---------------------------------------------
    # exit if PlugIn is not enabled
    # ---------------------------------------------
    if enabled != "1":
        sys.exit(-1)


    # ---------------------------------------------
    # Running in daemon mode
    # ---------------------------------------------
    if len(sys.argv) >= 2:

        # if called with argument "daemon"
        if sys.argv[1] == "daemon":

            # check if it is time to run - otherwise exit
            if (int(time.strftime("%H")) / pollFrequency).is_integer() == False:
                sys.exit(-1)


    # ---------------------------------------------
    # scan for Xiaomi MiFlora device
    # ---------------------------------------------
    log('Scanning for Xiaomi MiFlora devices (takes up to {0} seconds)'.format(scanTimeout))

    devices = miflora_scanner.scan(BluepyBackend, scanTimeout)
    
    log('Found {0} devices:'.format(len(devices)), "INFO")


    # ---------------------------------------------
    # if devices were found, remove cached data file
    # ---------------------------------------------
    if len(devices) >= 1:
        if os.path.isfile(lastdatafile):
            os.remove(lastdatafile)


    # ---------------------------------------------
    # Get data for each found sensor
    # ---------------------------------------------
    for device in devices:
        devicemac = device.replace(":", "")

        log('Polling device: {0}'.format(device), "INFO")

        poller = MiFloraPoller(device, BluepyBackend)

        # -------------------------------
        # Name
        # -------------------------------
        # build value string
        value = "{0}.{1}={2}".format(devicemac, "Name", poller.name())
        
        # log data
        log(value, "INFO")

        # write value to lastdata.dat
        writelastdata(lastdatafile, value)

        # send value as udp datagram
        sendudp(value, miniserverIP, virtualUDPPort)


        # -------------------------------
        # PollTime
        # -------------------------------
        # Calculate offset based on 01.01.2009
        loxBaseEpoch = 1230768000;

        # Use current time as polling time
        pollTime = int(time.time())


        # Convert time to localtime if enabled
        if localtime == "1":
            pollLocalTime = time.localtime(pollTime)

            pollTime = pollTime + pollLocalTime.tm_gmtoff


        # Subtract time / date offset
        loxSensorTime = pollTime - loxBaseEpoch;

        # build value strings
        value = "{0}.{1}={2}".format(devicemac, "PollTime", loxSensorTime)

        # log data
        log(value, "INFO")
        
        # write value to lastdata.dat
        writelastdata(lastdatafile, value)

        # send value as udp datagram
        sendudp(value, miniserverIP, virtualUDPPort)


        # -------------------------------
        # PollTime
        # -------------------------------
        # Use current time as polling time
        timestamp = time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(time.time()))

        # build value strings
        value = "{0}.{1}={2}".format(devicemac, "PollTimeString", timestamp)

        # log data
        log(value, "INFO")
        
        # write value to lastdata.dat
        writelastdata(lastdatafile, value)

        # send value as udp datagram
        sendudp(value, miniserverIP, virtualUDPPort)


        # -------------------------------
        # Firmware
        # -------------------------------
        # build value string
        value = "{0}.{1}={2}".format(devicemac, "Firmware", poller.firmware_version())

        # log data
        log(value, "INFO")
        
        # write value to lastdata.dat
        writelastdata(lastdatafile, value)

        # send value as udp datagram
        sendudp(value, miniserverIP, virtualUDPPort)


        # -------------------------------
        # Temperature
        # -------------------------------
        # build value string
        value = "{0}.{1}={2}".format(devicemac, "Temperature", poller.parameter_value(MI_TEMPERATURE))

        # log data
        log(value, "INFO")
        
        # write value to lastdata.dat
        writelastdata(lastdatafile, value)

        # send value as udp datagram
        sendudp(value, miniserverIP, virtualUDPPort)


        # -------------------------------
        # Moisture
        # -------------------------------
        # build value string
        value = "{0}.{1}={2}".format(devicemac, "Moisture", poller.parameter_value(MI_MOISTURE))

        # log data
        log(value, "INFO")
        
        # write value to lastdata.dat
        writelastdata(lastdatafile, value)

        # send value as udp datagram
        sendudp(value, miniserverIP, virtualUDPPort)


        # -------------------------------
        # Light
        # -------------------------------
        # build value string
        value = "{0}.{1}={2}".format(devicemac, "Light", poller.parameter_value(MI_LIGHT))

        # log data
        log(value, "INFO")
        
        # write value to lastdata.dat
        writelastdata(lastdatafile, value)

        # send value as udp datagram
        sendudp(value, miniserverIP, virtualUDPPort)


        # -------------------------------
        # Conductivity
        # -------------------------------
        # build value string
        value = "{0}.{1}={2}".format(devicemac, "Conductivity", poller.parameter_value(MI_CONDUCTIVITY))

        # log data
        log(value, "INFO")
        
        # write value to lastdata.dat
        writelastdata(lastdatafile, value)

        # send value as udp datagram
        sendudp(value, miniserverIP, virtualUDPPort)


        # -------------------------------
        # Battery
        # -------------------------------
        # build value string
        value = "{0}.{1}={2}".format(devicemac, "Battery", poller.parameter_value(MI_BATTERY))

        # log data
        log(value, "INFO")
        
        # write value to lastdata.dat
        writelastdata(lastdatafile, value)

        # send value as udp datagram
        sendudp(value, miniserverIP, virtualUDPPort)

        log('-------------------------------------------------', "INFO")


    # exit with errorlevel 0
    sys.exit(0)

# _______________________________________________________________________________________


def writelastdata(filename, data):
    lastdatahandle = open(filename, 'a')
    lastdatahandle.write("{0}\n".format(data))
    lastdatahandle.close()

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
        log("Sent bytes do not match - expected {0} : got {1}".format(data.__len__(), res), "ERROR")
        log("Packet-Payload {0}".format(data), "ERROR")
        sys.exit(-1)

# _______________________________________________________________________________________


def log(message, level="INFO"):
    timestamp = time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(time.time()))

    print("{0}  {1} {2}".format(timestamp, level, message))
# _______________________________________________________________________________________

main()
