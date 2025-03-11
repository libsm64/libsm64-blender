import threading
from . import zeth_inputs

thread_running = False
events = []

def _input_reader_thread():
    global thread_running
    global events
    while thread_running:
        events.append(zeth_inputs.get_gamepad())

def start_input_reader():
    global thread_running

    if thread_running:
        return

    thread_running = True
    thread = threading.Thread(target=_input_reader_thread)
    thread.daemon = True
    thread.start()

def stop_input_reader():
    global thread_running
    thread_running = False

CAM_TURN_EIGTH = 1.0 / 8.0
ZOOM_INCR = 0.5
JOYSTICK_TRESHOLD = 0.3

def sample_input_reader(mario_inputs):
    from . import config, input_value
    mario_inputs.camLookX = 0;
    mario_inputs.camLookZ = 0;
    if config['keyboard_control']:
        mario_inputs.stickX = input_value['RIGHT']*1 - input_value['LEFT']*1
        mario_inputs.stickY = input_value['DOWN']*1 - input_value['UP']*1
        mario_inputs.buttonA = input_value['A']
        mario_inputs.buttonB = input_value['B']
        mario_inputs.buttonZ = input_value['C']
    else:
        while len(events) > 0 :
            for event in events[0]:
                if event.code == "ABS_X":
                    mario_inputs.stickX = _read_axis(float(event.state))
                elif event.code == "ABS_Y":
                    mario_inputs.stickY = _read_axis(float(event.state))
                elif event.code == "BTN_SOUTH":
                    if event.state == 1:
                        mario_inputs.buttonA = True
                    else:
                        mario_inputs.buttonA = False
                elif event.code == "BTN_NORTH":
                    if event.state == 1:
                        mario_inputs.buttonB = True
                    else:
                        mario_inputs.buttonB = False
                elif event.code == "BTN_TL":
                    if event.state == 1:
                        mario_inputs.buttonZ = True
                    else:
                        mario_inputs.buttonZ = False
                if event.code == "ABS_RX": # pan
                    stick_magnitude = _read_axis(float(event.state))
                    if stick_magnitude > JOYSTICK_TRESHOLD:
                      next = CAM_TURN_EIGTH
                    elif stick_magnitude < -JOYSTICK_TRESHOLD:
                      next = -CAM_TURN_EIGTH
                    else:
                      next = 0
                    mario_inputs.camLookX = next
                elif event.code == "ABS_RY": # zoom
                    stick_magnitude = _read_axis(float(event.state))
                    if stick_magnitude > JOYSTICK_TRESHOLD:
                      next = ZOOM_INCR
                    elif stick_magnitude < -JOYSTICK_TRESHOLD:
                      next = -ZOOM_INCR
                    else:
                      next = 0
                    mario_inputs.camLookZ = next
                #elif event.code != "SYN_REPORT":
                #    print(event.code + ':' + str(event.state))
            events.pop(0)

def _read_axis(val):
    val /= 32768.0
    if val < 0.2 and val > -0.2:
        return 0
    return (val - 0.2) / 0.8 if val > 0.0 else (val + 0.2) / 0.8
