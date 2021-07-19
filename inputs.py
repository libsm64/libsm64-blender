import os
import evdev

device: evdev.InputDevice = None #type:ignore

def inputs_initialize():
    global device
    device_list = evdev.list_devices()
    if (len(device_list) > 0):
        device = evdev.InputDevice(device_list[0])

def inputs_read():
    global device
    buttons = device.active_keys()
    print(buttons)
    return {
        'x_axis': (device.absinfo(0).value - 128) / 128,
        'y_axis': (device.absinfo(1).value - 128) / 128,
        'button_a': 304 in buttons,
        'button_b': 307 in buttons,
        'button_z': 310 in buttons,
    }
