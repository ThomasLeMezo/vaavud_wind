#!/usr/bin/env python3

# https://gist.github.com/ukBaz/0294521185af72c53f75903fbfb0adb5

import pydbus
from pydbus import SystemBus
from gi.repository import GLib
import sys
import time

DEVICE_ADDR = 'D4:DA:FE:8C:7C:EF'
UUID_BASE = '-0000-1000-8000-00805f9b34fb'

UUID_DEVICE_NAME = '2A29'
UUID_DEVICE_MODEL = '2A24'
UUID_FIRMWARE = '2A26'
UUID_DATA = '2A39'
UUID_STATUS = 'A001'
UUID_DATA_RATE = 'A002'
UUID_SENSORS = 'A003'
UUID_ANGLE_OFFSET = 'A007'
UUID_ECOMPAS_CALIB = 'A008'
UUID_WIND_CORREC = 'A009'

# DBus object paths
BLUEZ_SERVICE = 'org.bluez'
ADAPTER_PATH = '/org/bluez/hci0'
device_path = f"{ADAPTER_PATH}/dev_{DEVICE_ADDR.replace(':', '_')}"


def get_uuid(register):
    return '0000' + register + UUID_BASE

def get_characteristic_path(dev_path, uuid):
    """Look up DBus path for characteristic UUID"""
    mng_objs = mngr.GetManagedObjects()
    for path in mng_objs:
        chr_uuid = mng_objs[path].get('org.bluez.GattCharacteristic1', {}).get('UUID')
        if path.startswith(dev_path) and chr_uuid == uuid.casefold():
           return path

def get_data(bus, path):
    calypso = bus.get(BLUEZ_SERVICE, path)
    data = calypso.ReadValue({})
    return data

def convert_device_name(raw_data):
    print("DEVICE_NAME = ", ''.join(chr(i) for i in raw_data))

def convert_device_model(raw_data):
    print("DEVICE_MODE = ", ''.join(chr(i) for i in raw_data))

def convert_firmawre(raw_data):
    print("DEVICE_FIRMWARE = ", ''.join(chr(i) for i in raw_data))

def convert_measures(raw_data):
    velocity = ((raw_data[1]<<4) + raw_data[0])/100
    wind_direction = ((raw_data[3]<<4) + raw_data[2])
    battery_level = raw_data[4]*10
    temp_level = raw_data[5]-100
    roll = raw_data[6]-90
    pitch = raw_data[7]-90
    ecompass = 360-((raw_data[8]<<4) + raw_data[0])

    print(time.time(), velocity, wind_direction, battery_level, temp_level, roll, pitch, ecompass)

def convert_status(raw_data):
    if(raw_data==0x00):
        print("Sleep Mode, Only Advertising")
    if(raw_data==0x01):
        print("Low Power Mode, 1hz and Sensors disabled")
    if(raw_data==0x02):
        print("Normal Mode, All data rate and sensors availables")

def convert_measures_rate(raw_data):
    print("MEASURE_RATE = ", str(int(raw_data[0])) + "Hz")

def convert_sensor_clinometer(raw_data):
    print("ENABLE_CLINOMETER = ", "ON" if raw_data==0x01 else "OFF")

def convert_angle_offset(raw_data):
    print("ANGLE_OFFSET = ",raw_data[1]<<4 + raw_data[0])

def convert_ecompass_mode(raw_data):
    print("MODE = ", "Calibration" if raw_data==0x01 else "Normal")

def convert_wind_corr(raw_data):
    val = 0
    for i in range(4):
        val += (raw_data[i]<<((3-i)*4))
    print("WIND_CORR = ", val/32.0)

def get_device_name(bus):
    raw_data = get_data(bus, calypso_DEVICE_NAME_path)
    convert_device_name(raw_data)

def get_device_model(bus):
    raw_data = get_data(bus, calypso_DEVICE_MODEL_path)
    convert_device_model(raw_data)

def get_firmawre(bus):
    raw_data = get_data(bus, calypso_FIRMWARE_path)
    convert_firmawre(raw_data)

def get_measures(bus):
    raw_data = get_data(bus, calypso_MEASURES_path)
    convert_measures(raw_data)

def get_status(bus):
    raw_data = get_data(bus, calypso_STATUS_path)
    convert_status(raw_data)

def get_measures_rate(bus):
    raw_data = get_data(bus, calypso_MEASURES_RATE_path)
    convert_measures_rate(raw_data)

def get_sensor_clinometer(bus):
    raw_data = get_data(bus, calypso_SENSORS_path)
    convert_sensor_clinometer(raw_data)

def get_angle_offset(bus):
    raw_data = get_data(bus, calypso_ANGLE_OFFSET_path)
    convert_angle_offset(raw_data)

def get_ecompass_mode(bus):
    raw_data = get_data(bus, calypso_ECOMPAS_CALIB_path)
    convert_ecompass_mode(raw_data)

def get_wind_corr(bus):
    raw_data = get_data(bus, calypso_WIND_CORREC_path)
    convert_wind_corr(raw_data)


# Enable eventloop for notifications
def measure_handler(iface, prop_changed, prop_removed):
    """Notify event handler for button press"""
    if 'Value' in prop_changed:
        new_value = prop_changed['Value']
        #print(f"Button A state: {new_value}")
        convert_measures(new_value)

###############################################

# setup dbus
bus = pydbus.SystemBus()
mngr = bus.get(BLUEZ_SERVICE, '/')
adapter = bus.get(BLUEZ_SERVICE, ADAPTER_PATH) 
device = bus.get(BLUEZ_SERVICE, device_path)

device.Connect()

while not device.ServicesResolved:
    sleep(0.5)


# Characteristic DBus information
calypso_DEVICE_NAME_path = get_characteristic_path(device._path, get_uuid(UUID_DEVICE_NAME))
calypso_DEVICE_MODEL_path = get_characteristic_path(device._path, get_uuid(UUID_DEVICE_MODEL))
calypso_FIRMWARE_path = get_characteristic_path(device._path, get_uuid(UUID_FIRMWARE))
calypso_MEASURES_path = get_characteristic_path(device._path, get_uuid(UUID_DATA))
calypso_STATUS_path = get_characteristic_path(device._path, get_uuid(UUID_STATUS))
calypso_MEASURES_RATE_path = get_characteristic_path(device._path, get_uuid(UUID_DATA_RATE))
calypso_SENSORS_path = get_characteristic_path(device._path, get_uuid(UUID_SENSORS))
calypso_ANGLE_OFFSET_path = get_characteristic_path(device._path, get_uuid(UUID_ANGLE_OFFSET))
calypso_ECOMPAS_CALIB_path = get_characteristic_path(device._path, get_uuid(UUID_ECOMPAS_CALIB))
calypso_WIND_CORREC_path = get_characteristic_path(device._path, get_uuid(UUID_WIND_CORREC))

get_device_name(bus)
get_device_model(bus)
get_firmawre(bus)
get_measures(bus)
get_status(bus)
get_measures_rate(bus)
get_sensor_clinometer(bus)
get_angle_offset(bus)
get_ecompass_mode(bus)
get_wind_corr(bus)
        

# Handler
mainloop = GLib.MainLoop()
calypso = bus.get(BLUEZ_SERVICE, calypso_MEASURES_path)
calypso.onPropertiesChanged = measure_handler
calypso.StartNotify()

mainloop.run()
    
mainloop.quit()
calypso.StopNotify()
device.Disconnect()
